// set the dimensions and margins of the graph
var margin = {top: 80, right: 25, bottom: 30, left: 40},
  width = 800 - margin.left - margin.right,
  height = 5000 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#heatmap-container")
  .html(null)
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

//Read the data
const urlParams = new URLSearchParams(window.location.search);
const dataSha = urlParams.get('data_sha');
// Get the current page URL
const currentUrl = window.location.href;
// Extract the 'owner' part from the GitHub Pages URL
const matches = currentUrl.match(/^https:\/\/([^\.]+)\.github\.io\/([^\/]+)/);
const owner = (matches && matches.length === 3) ? matches[1] : 'FCP-INDI';
const dataUrl = `https://raw.githubusercontent.com/${owner}/regtest-runlogs/C-PAC_${dataSha}/correlations.json`
datasource = d3.json(dataUrl);
datasource.then(function(data) {

  data.sort(function(a, b) { return d3.descending(a.rowid, b.rowid) });
  // Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
  var groupedData = d3.group(data, d => d.columnid);
  var myGroups = Array.from(groupedData.keys());
  var myVars = Array.from(d3.group(data, d => d.rowid).keys());

  // Build X scales and axis:
  var x = d3.scaleBand()
    .domain(myGroups)
    .range([0, width])
    .padding(0.05);

  svg.append("g")
    .style("font-size", 15)
    .attr("transform", "translate(0,0)")
    .call(d3.axisTop(x).tickSize(0))
    .select(".domain").remove();

  // Build Y scales and axis:
  var y = d3.scaleBand()
    .domain(myVars)
    .range([height, 0])
    .padding(0.05);

  svg.append("g")
    .style("font-size", 15)
    .attr("transform", "translate(" + width + ",0)")
    .call(d3.axisLeft(y).tickSize(0))
    .select(".domain").remove();

  // Build color scale
  var myColor = d3.scaleSequential()
    .interpolator(d3.interpolateRdYlGn)
    .domain([0.8, 1]);

  // Create a tooltip
  var tooltip = d3.select("#my_dataviz")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip")
    .style("background-color", "white")
    .style("border", "solid")
    .style("border-width", "2px")
    .style("border-radius", "5px")
    .style("padding", "5px");

  // Three functions that change the tooltip when user hovers / moves / leaves a cell
  var mouseover = function(d) {
    tooltip
      .style("opacity", 1);
    d3.select(this)
      .style("stroke", "black")
      .style("opacity", 1);
  };

  var mousemove = function(d) {
    tooltip
      .html(d.rowid + ": " + d.value)
      .style("left", (d3.pointer(this)[0] + 70) + "px")
      .style("top", (d3.pointer(this)[1]) + "px");
  };

  var mouseleave = function(d) {
    tooltip
      .style("opacity", 0);
    d3.select(this)
      .style("stroke", "none")
      .style("opacity", 0.8);
  };

  // Add the squares
  svg.selectAll()
    .data(data, function(d) {return d.columnid + ':' + d.variable;})
    .enter()
    .append("rect")
      .attr("x", function(d) { return x(d.columnid) + (x.bandwidth() / 2); })
      .attr("y", function(d) { return y(d.rowid); })
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("width", y.bandwidth())
      .attr("height", y.bandwidth())
      .style("fill", function(d) { return myColor(d.value); })
      .style("stroke-width", 0)
      .style("stroke", "none")
      .style("opacity", 0.8)
    .on("mouseover", mouseover)
    .on("mousemove", mousemove)
    .on("mouseleave", mouseleave);
});

// Add title to graph
svg.append("text")
  .attr("x", 0)
  .attr("y", -50)
  .attr("text-anchor", "left")
  .style("font-size", "22px")
  .text("GRAPHTITLE");

// Add subtitle to graph
svg.append("text")
  .attr("x", 0)
  .attr("y", -20)
  .attr("text-anchor", "left")
  .style("font-size", "14px")
  .style("fill", "grey")
  .style("max-width", 400)
  .text("GRAPHSUBTITLE");