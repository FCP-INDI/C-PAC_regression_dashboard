function getTextWidth(text, fontSize) {
  const svg = d3.select("body").append("svg").attr("height", 0);
  const textElement = svg.append("text").attr("font-size", fontSize).text(text);
  const width = textElement.node().getComputedTextLength();
  svg.remove(); // Remove the temporary SVG element
  return width;
}

const margin = { top: 80, right: 25, bottom: 60, left: 40 };
const squareSize = 16;

const urlParams = new URLSearchParams(window.location.search);
const dataSha = urlParams.get("data_sha");
const currentUrl = window.location.href;
const matches = currentUrl.match(/^https:\/\/([^\.]+)\.github\.io\/([^\/]+)/);
const owner = matches && matches.length === 3 ? matches[1] : "FCP-INDI";
const dataUrl = `https://raw.githubusercontent.com/${owner}/regtest-runlogs/C-PAC_${dataSha}/correlations.json`;

d3.json(dataUrl).then(function (allData) {
  // Group by preconfig if available
  const hasPreconfig = allData.some((d) => d.preconfig !== undefined);
  const grouped = hasPreconfig
    ? d3.group(allData, (d) => d.preconfig)
    : new Map([["", allData]]); // fallback single group

  const container = d3.select("#heatmap-container").html(null);

  grouped.forEach((data, preconfig) => {
    data.sort((a, b) => d3.descending(a.rowid, b.rowid));
    const myGroups = Array.from(d3.group(data, (d) => d.columnid).keys());
    const myVars = Array.from(d3.group(data, (d) => d.rowid).keys());

    const xLabelWidth = d3.max(myGroups, (d) => getTextWidth(d, "15px") + 15);
    const yLabelWidth = d3.max(myVars, (d) => getTextWidth(d, "15px") + 15);

    const heatWidth = myGroups.length * squareSize;
    const heatHeight = myVars.length * squareSize;

    const svg = container
      .append("div")
      .style("margin-bottom", "100px")
      .append("svg")
      .attr("width", heatWidth + margin.left + yLabelWidth + margin.right)
      .attr(
        "height",
        heatHeight + margin.top + xLabelWidth + margin.bottom + 60,
      ) // extra for legend
      .append("g")
      .attr(
        "transform",
        `translate(${margin.left + yLabelWidth},${margin.top + xLabelWidth})`,
      );

    const x = d3.scaleBand().domain(myGroups).range([0, heatWidth]).padding(0);

    const y = d3.scaleBand().domain(myVars).range([heatHeight, 0]).padding(0);

    const myColor = d3
      .scaleSequential()
      .interpolator(d3.interpolateRdYlGn)
      .domain([0.8, 1.001]);

    const tooltip = container
      .append("div")
      .classed("tooltip", true)
      .style("opacity", 0);

    // Axes
    svg
      .append("g")
      .style("font-size", 15)
      .call(d3.axisTop(x).tickSize(0))
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", "0.5em")
      .attr("transform", "rotate(90)");

    svg
      .append("g")
      .style("font-size", 15)
      .call(d3.axisLeft(y).tickSize(0))
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", ".15em");

    // Squares
    svg
      .selectAll()
      .data(data, (d) => d.columnid + ":" + d.rowid)
      .enter()
      .append("rect")
      .attr("x", (d) => x(d.columnid))
      .attr("y", (d) => y(d.rowid) + (y.bandwidth() - squareSize) / 2)
      .attr("width", squareSize)
      .attr("height", squareSize)
      .attr("rx", 4)
      .attr("ry", 4)
      .attr("value", (d) => Math.round(d.value * 1e6) / 1e6)
      .attr("columnid", (d) => d.columnid)
      .attr("rowid", (d) => d.rowid)
      .style("fill", (d) => myColor(d.value))
      .style("stroke", "none")
      .on("mouseover", function (e) {
        const [mouseX, mouseY] = d3.pointer(e);
        const rect = d3.select(this);
        rect.style("fill", "grey");
        tooltip
          .style("opacity", 1)
          .style("background-color", myColor(rect.attr("value")))
          .html(rect.attr("rowid") + ": " + rect.attr("value"))
          .style("left", mouseX + squareSize + margin.left + yLabelWidth + "px")
          .style("top", mouseY + squareSize + margin.top + xLabelWidth + "px");
      })
      .on("mousemove", function (e) {
        const [mouseX, mouseY] = d3.pointer(e);
        const rect = d3.select(this);
        tooltip
          .html(rect.attr("rowid") + ": " + rect.attr("value"))
          .style("opacity", 1)
          .style("left", mouseX + squareSize + margin.left + yLabelWidth + "px")
          .style("top", mouseY + margin.top + xLabelWidth + "px");
      })
      .on("mouseleave", function (d) {
        d3.select(this).style("fill", (d) => myColor(d.value));
        tooltip.style("opacity", 0);
      });

    // Title
    svg
      .append("text")
      .attr("x", -yLabelWidth)
      .attr("y", -(xLabelWidth + 50))
      .attr("text-anchor", "left")
      .style("font-size", "22px")
      .text(
        `C-PAC regression test correlations${
          preconfig ? " (" + preconfig + ")" : ""
        }`,
      );

    // Subtitle with link
    svg
      .append("a")
      .attr("href", `https://github.com/FCP-INDI/C-PAC/commit/${dataSha}`)
      .append("text")
      .attr("x", -yLabelWidth)
      .attr("y", -(xLabelWidth + 20))
      .attr("text-anchor", "left")
      .style("font-size", "14px")
      .style("fill", "grey")
      .text(dataSha);

    // Legend
    const legendWidth = 200;
    const legendHeight = 10;

    const defs = svg.append("defs");
    const linearGradient = defs
      .append("linearGradient")
      .attr("id", `legend-gradient-${preconfig || "default"}`);

    linearGradient
      .selectAll("stop")
      .data(
        d3.range(0, 1.01, 0.01).map((d) => ({
          offset: `${d * 100}%`,
          color: myColor(0.8 + 0.201 * d),
        })),
      )
      .enter()
      .append("stop")
      .attr("offset", (d) => d.offset)
      .attr("stop-color", (d) => d.color);

    const legendGroup = svg
      .append("g")
      .attr(
        "transform",
        `translate(${(heatWidth - legendWidth) / 2},${heatHeight + 40})`,
      );

    legendGroup
      .append("rect")
      .attr("width", legendWidth)
      .attr("height", legendHeight)
      .style("fill", `url(#legend-gradient-${preconfig || "default"})`);

    const legendScale = d3
      .scaleLinear()
      .domain([0.8, 1.0])
      .range([0, legendWidth]);

    const legendAxis = d3
      .axisBottom(legendScale)
      .ticks(5)
      .tickFormat(d3.format(".2f"));

    legendGroup
      .append("g")
      .attr("transform", `translate(0,${legendHeight})`)
      .call(legendAxis)
      .style("font-size", "12px");
  });
});
