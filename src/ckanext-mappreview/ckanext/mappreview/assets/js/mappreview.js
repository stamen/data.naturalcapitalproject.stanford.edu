ckan.module("mappreview", function ($, _) {
  "use strict";
  return {
    options: {
      config: {},
      globalConfig: {},
      debug: false,
      titilerUrl: 'https://titiler-897938321824.us-west1.run.app',
    },

    _getGlobalConfig: function () {
      return JSON.parse(this.options.globalConfig.replace(/'/g, '"'));
    },

    _getRasterTilejsonUrl: function (layer) {
      const base = this._getGlobalConfig().titiler_url;
      const endpoint = '/cog/WebMercatorQuad/tilejson.json';

      // Generate custom color map
      const colors = [
        '#6DB31E',
        '#008F5F',
        '#00646E',
        '#1C3A6D',
        '#27003B',
      ];

      let steps = [];

      colors.forEach((c, i) => {
        if (i === colors.length - 1) return;

        const c1 = new Color(colors[i]);
        const c2 = new Color(colors[i + 1]);

        const innerSteps = c1.steps(c2, {
          space: 'lch',
          steps: Math.ceil(256 / (colors.length - 1)),
          outputSpace: 'srgb',
        });

        steps = steps.concat(innerSteps);
      });

      const rgbas = steps.map((c, i) => {
        return [
          ...c.coords.map(coord => Math.floor(coord * 255)),
          i <= 6 ? 50 : 255
          // 255
        ];
      });

      const colormap = rgbas.map((rgba, i) => [[i, i + 1], rgba]);

      const params = {
        tile_scale: 2,
        url: layer.url,
        bidx: 1,
        rescale: `${layer.pixel_min_value},${layer.pixel_max_value}`,
        // rescale: `${layer.pixel_percentile_2},${layer.pixel_percentile_98}`,
        colormap: JSON.stringify(colormap),
        // colormap_name: 'viridis_r',
        // colormap_name: 'viridis_r',
        // colormap_name: 'blues',
      };

      const paramsPrepared = Object.entries(params)
        .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
        .join('&');

      return `${base}${endpoint}?${paramsPrepared}`;
    },

    _getRasterLayer: function (layer) {
      return {
        id: layer.name,
        type: 'raster',
        source: layer.name,
        paint: {
          'raster-opacity': ['interpolate', ['linear'], ['zoom'], 0, 0.75, 12, 1],
        },
      };
    },

    initialize: function () {
      jQuery.proxyAll(this, '_getGlobalConfig');
      jQuery.proxyAll(this, '_getRasterLayer');
      jQuery.proxyAll(this, '_getRasterTilejsonUrl');

      const config = JSON.parse(this.options.config.replace(/'/g, '"'));
      const globalConfig = this._getGlobalConfig();

      mapboxgl.accessToken = globalConfig.mapbox_api_key;
      const map = new mapboxgl.Map({
        container: 'map',
        style: globalConfig.mapbox_style,
        bounds: config.map.bounds,
        minZoom: config.map.minzoom + 2,
        maxZoom: config.map.maxzoom,
      });

      const sources = config.layers.map(l => {
        if (l.type === 'raster') {
          const url = this._getRasterTilejsonUrl(l);
          return {
            id: l.name,
            type: 'raster',
            url,
          };
        }
      });

      const layers = config.layers.map(l => {
        if (l.type === 'raster') {
          return this._getRasterLayer(l);
        }
      });

      map.on('load', () => {
        sources.forEach((source) => {
          map.addSource(source.id, source);
        });

        layers.forEach((layer) => {
          map.addLayer(layer);
        });

        const targets = Object.fromEntries(config.layers.map(l => [l.name, l.name]));

        map.addControl(new MapboxLegendControl(targets, {
          showDefault: false, 
          showCheckbox: true, 
          onlyRendered: false,
          reverseOrder: true
        }), 'top-right');
      });

      // TODO only for vector layers?
      map.on('click', sources.map(s => s.id), (e) => {
        let content = '';

        e.features.forEach(f => {
          content += `<h3>${f.layer.id}</h3>
            <ul>
            ${Object.keys(f.properties).map(k => `<li>${k}: ${f.properties[k]}</li>`).join('')}
          </ul>`;
        });

        const popup = new mapboxgl.Popup({ className: 'mappreview-mapboxgl-popup' })
          .setLngLat(e.lngLat)
          .setMaxWidth("300px")
          .setHTML(content)
          .addTo(map);
      });
    },
  };
});
