ckan.module("mappreview", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
    },

    initialize: function () {
      mapboxgl.accessToken = 'pk.eyJ1Ijoic3RhbWVuIiwiYSI6ImNtMWkzNm16ZzBsZDYya3B4anI5cG9tN3kifQ.i91AOKPswRy5EA1zi7PO-w';
      const map = new mapboxgl.Map({
          container: 'map',
          center: [-122.420679, 37.772537],
          zoom: 13,
          style: 'mapbox://styles/mapbox/light-v11',
          bounds: [-79.365234,23.120154,-76.453857,25.849337],
      });

      const sources = [
        { id: 'airport', url: '/data/recreation/airport.geojson' },
        { id: 'dredged-ports', url: '/data/recreation/dredged-ports.geojson' },
        { id: 'beaches', url: '/data/recreation/beaches.geojson' },
        { id: 'roads-simple', url: '/data/recreation/roads-simple.geojson' },
        { id: 'roads-simple-buf', url: '/data/recreation/roads-simple-buf.geojson' },
        { id: 'bonefish', url: '/data/recreation/bonefish.geojson' },
        { id: 'andros-aoi', url: '/data/recreation/andros-aoi.geojson' },
      ];

      map.on('load', () => {
        sources.forEach((source) => {
          map.addSource(source.id, {
            type: 'geojson',
            data: source.url,
          });
        });

        map.addLayer({
          id: 'andros-aoi',
          type: 'fill',
          source: 'andros-aoi',
          paint: {
            'fill-color': '#0088ff',
            'fill-opacity': 0.2,
          },
        });

        map.addLayer({
          id: 'bonefish',
          type: 'fill',
          source: 'bonefish',
          paint: {
            'fill-color': '#ff44ef',
            'fill-opacity': 0.2,
          },
        });

        map.addLayer({
          id: 'roads-simple-buf',
          type: 'fill',
          source: 'roads-simple-buf',
          paint: {
            'fill-color': '#91522d',
            'fill-opacity': 0.5,
          },
        });

        map.addLayer({
          id: 'beaches',
          type: 'line',
          source: 'beaches',
          paint: {
            'line-color': 'brown',
            'line-opacity': 1,
            'line-width': 2,
          },
        });

        map.addLayer({
          id: 'roads-simple',
          type: 'line',
          source: 'roads-simple',
          paint: {
            'line-color': 'black',
            'line-opacity': 0.5,
            'line-width': 0.5,
          },
        });

        map.addLayer({
          id: 'airport',
          type: 'circle',
          source: 'airport',
          paint: {
            'circle-color': '#ff0000',
            'circle-radius': 5,
          },
        });

        map.addLayer({
          id: 'dredged-ports',
          type: 'circle',
          source: 'dredged-ports',
          paint: {
            'circle-color': '#00ff00',
            'circle-radius': 5,
          },
        });

        const targets = {
          'andros-aoi': 'Andros AOI',
          'bonefish': 'Bonefish',
          'beaches': 'Beaches',
          'roads-simple': 'Roads',
          'roads-simple-buf': 'Roads Buffer',
          'dredged-ports': 'Dredged Ports',
          'airport': 'Airport',
        };

        map.addControl(new MapboxLegendControl(targets, {
          showDefault: false, 
          showCheckbox: true, 
          onlyRendered: false,
          reverseOrder: true
        }), 'top-right');
      });

      map.on('click', sources.map(s => s.id), (e) => {
        console.log(e.features);
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
