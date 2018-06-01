/*global google,fetch*/
google.charts.load('current', {'packages':['gantt']});
const chartsLoaded = new Promise(resolve => google.charts.setOnLoadCallback(resolve));
const domLoaded = new Promise(resolve => {
  function loaded() {
    window.removeEventListener('DOMContentLoaded', loaded);
    resolve();
  }
  window.addEventListener('DOMContentLoaded', loaded);
});

function loadUrlJSON(url) {
  return fetch(url).then(res => res.json());
}

function daysToMilliseconds(days) {
  return days * 24 * 60 * 60 * 1000;
}

function drawChart(build_data) {
  console.dir(build_data);
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Task ID');
  data.addColumn('string', 'Task Name');
  data.addColumn('date', 'Start Date');
  data.addColumn('date', 'End Date');
  data.addColumn('number', 'Duration');
  data.addColumn('number', 'Percent Complete');
  data.addColumn('string', 'Dependencies');

  data.addRows(build_data);
  var chart = new google.visualization.Gantt(document.getElementById('chart_div'));
  //FIXME: it would be nice if the chart could figure out its own height.
  chart.draw(data, {height: 20000});
}


function makeDataRow(start, round, i, item) {
  const s = start + round * 1000;
  const name = `${item.package_name} ${item.package_version} ${item.target_kind[0]} ${item.kind}`;
  return [i.toString(), name, new Date(s), new Date(s + 1000), null, 100, item.deps.join(',')];
}

function parseData(data) {
  console.log('Loaded %d invocations', data.invocations.length);
  const start = Date.now();
  var output = [];
  var seen = new Set();
  var invocations = new Map(data.invocations.entries());
  var round = 0;
  while (invocations.size > 0) {
    var next_seen = new Set();
    for (var [i, item] of invocations.entries()) {
      if (!item.deps.every(d => seen.has(d))) {
        continue;
      }
      output.push(makeDataRow(start, round, i, item));
      next_seen.add(i);
      invocations.delete(i);
    }
    console.log('Round %d: %d items seen', round, next_seen.size);
    round++;
    for (var s of next_seen) {
      seen.add(s);
    }
  }
  return output;
}

Promise.all([chartsLoaded, domLoaded, loadUrlJSON('data.json')]).then(([c,d,data]) => {
  drawChart(parseData(data));
});

