function getTextWidth(text, fontSize) {
  var svg = d3.select("body").append("svg").attr("height", 0);
  var textElement = svg.append("text").attr("font-size", fontSize).text(text);
  var width = textElement.node().getComputedTextLength();
  svg.remove(); // Remove the temporary SVG element
  return width;
}

// set the dimensions and margins of the graph
var margin = { top: 80, right: 25, bottom: 30, left: 40 },
  width = 800 - margin.left - margin.right,
  height = 5000 - margin.top - margin.bottom;

let svg;

//Read the data
const urlParams = new URLSearchParams(window.location.search);
const dataSha = urlParams.get("data_sha");
// Get the current page URL
const currentUrl = window.location.href;
// Extract the 'owner' part from the GitHub Pages URL
const matches = currentUrl.match(/^https:\/\/([^\.]+)\.github\.io\/([^\/]+)/);
const owner = matches && matches.length === 3 ? matches[1] : "shnizzedy"; // 'FCP-INDI';
const dataUrl = `https://raw.githubusercontent.com/${owner}/regtest-runlogs/C-PAC_${dataSha}/correlations.json`;
datasource = d3.json(dataUrl);
datasource.then(function (data) {
  data.sort(function (a, b) {
    return d3.descending(a.rowid, b.rowid);
  });
  // Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
  var groupedData = d3.group(data, (d) => d.columnid);
  var myGroups = Array.from(groupedData.keys());
  var myVars = Array.from(d3.group(data, (d) => d.rowid).keys());

  // Build X scales and axis:
  var x = d3
    .scaleBand()
    .domain(myGroups)
    .range([0, myGroups.length]) // Adjusted the range
    .paddingInner(0) // Removed inner padding
    .paddingOuter(0); // Removed outer padding

  // Build Y scales and axis:
  var y = d3.scaleBand().domain(myVars).range([height, 0]).padding(0.05);

  // Calculate the maximum width of the y-axis labels before creating the SVG
  const yLabelWidth = d3.max(myVars, function (varName) {
    return getTextWidth(varName, "15px") + 15;
  });

  // Build color scale
  var myColor = d3
    .scaleSequential()
    .interpolator(d3.interpolateRdYlGn)
    .domain([0.8, 1]);

  svg = d3
    .select("#heatmap-container")
    .html(null)
    .append("svg")
    .attr("width", width + margin.left + margin.right + yLabelWidth) // Updated the width
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr(
      "transform",
      "translate(" +
        (margin.left + 2 * margin.right + yLabelWidth) +
        "," +
        margin.top +
        ")",
    ); // Updated the translation

  // Build Y scales and axis:
  var y = d3.scaleBand().domain(myVars).range([height, 0]).padding(0.05);

  // Build color scale
  var myColor = d3
    .scaleSequential()
    .interpolator(d3.interpolateRdYlGn)
    .domain([0.8, 1]);

  // Create a tooltip
  const tooltip = d3
    .select("#heatmap-container")
    .append("div")
    .classed("tooltip", true);

  // Add the adjusted x-axis with rotated labels
  svg
    .append("g")
    .style("font-size", 15)
    .attr("transform", "translate(0, 0)") // Adjusted the translation
    .call(d3.axisTop(x).tickSize(0))
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("transform", "rotate(90)");

  // Add the adjusted y-axis
  svg
    .append("g")
    .style("font-size", 15)
    .call(d3.axisLeft(y).tickSize(0))
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em");

  // Add the squares
  svg
    .selectAll()
    .data(data, function (d) {
      return d.columnid + ":" + d.variable;
    })
    .enter()
    .append("rect")
    .attr("columnid", function (d) {
      return d.columnid;
    })
    .attr("rowid", function (d) {
      return d.rowid;
    })
    .attr("value", function (d) {
      return d.value;
    })
    .attr("x", function (d) {
      return myGroups.length - x(d.columnid) - x.bandwidth();
    }) // Adjusted x-coordinate
    .attr("y", function (d) {
      return y(d.rowid);
    })
    .attr("rx", 4)
    .attr("ry", 4)
    .attr("width", y.bandwidth()) // Set the width to match the height
    .attr("height", y.bandwidth())
    .style("fill", function (d) {
      return myColor(d.value);
    })
    .style("stroke-width", 0)
    .style("stroke", "none")
    .style("opacity", 0.8)
    .on("mouseover", function (e) {
      const [mouseX, mouseY] = d3.pointer(e);
      const rect = d3.select(this);
      tooltip
        .style("opacity", 1)
        .style("background-color", myColor(rect.attr("value")))
        .html(rect.attr("rowid") + ": " + rect.attr("value"))
        .style("right", mouseX + "px")
        // .style("left", (mouseX + (yLabelWidth / 3)) + "px")
        .style("top", mouseY + 100 + "px");
    })
    .on("mousemove", function (e) {
      const [mouseX, mouseY] = d3.pointer(e);
      const rect = d3.select(this);
      tooltip
        .html(rect.attr("rowid") + ": " + rect.attr("value"))
        .style("opacity", 1)
        .style("right", mouseX + "px")
        // .style("left", (mouseX + (yLabelWidth / 3)) + "px")
        .style("top", mouseY + 100 + "px");
    })
    .on("mouseleave", function (d) {
      tooltip.style("opacity", 0);
    });

  // Add title to graph
  svg
    .append("text")
    .attr("x", -yLabelWidth)
    .attr("y", -50)
    .attr("text-anchor", "left")
    .style("font-size", "22px")
    .text("C-PAC regression test correlations");

  // Add subtitle to graph
  svg
    .append("text")
    .attr("x", -yLabelWidth)
    .attr("y", -20)
    .attr("text-anchor", "left")
    .style("font-size", "14px")
    .style("fill", "grey")
    .style("max-width", 400)
    .text(dataSha);
});
