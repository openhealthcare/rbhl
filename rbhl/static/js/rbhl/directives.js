directives.directive("peakFlowGraph", function($timeout, displayDateFilter) {
  "use strict";

  return {
    scope: {
      data: "=",
      highlights: "="
    },
    link: function(scope, element, attrs) {
      let data = scope.data;
      // the doctors tell us above 15 is considered significant
      const UPPER_BOUND = 15;

      let getLineData = function(days, title, name){
        let values = _.pluck(days, name);
        values = values.map(value => {
          if(_.isUndefined(value)){
            return null;
          }
          return value;
        });
        return [title].concat(values)
      }
      // make sure we don't call it too many times during the render
      let render_chart = function() {
          let days = data.days;
          let x = getLineData(days, "x", "day_num");
          let mean = getLineData(days, "Mean", "mean_flow");
          let max = getLineData(days, "Max", "max_flow");
          let min = getLineData(days, "Min", "min_flow");
          let pef = getLineData(days, "Predicted PF", "pef_flow")

          scope.completeness = data.completeness;
          scope.overrall_mean = data.overrall_mean;
          scope.pef_mean = data.pef_mean;

        // We want to colour days when the person was at work to easily identify them
        // It's _occupational_ lung disease after all.
        let working_days = _.map(
          _.filter(days, function(day) {
            return day.work_day;
          }),
          function(day) {
            return day.day_num;
          }
        );

        working_days.sort(function(a, b) {
          return a - b;
        });

        let calculateGridLines = function(trialDays) {
          /*
           * the grid lines should be intra file day not
           * on the day itself
           */
          let gridLinesMax = _.max(trialDays);
          let gridLinesMin = _.min(trialDays);
          let range = _.range(gridLinesMin - 0.5, gridLinesMax + 0.5, 1);
          return _.map(range, function(r) {
            return {
              value: r,
              class: "c3-dashed-line"
            };
          });
        };

        let gridLines = calculateGridLines(x);
        let sequences = [];

        let find_sequences = function(data) {
          let sequence = data[0],
            items = data[1];

          if (items.length == 0) {
            return;
          }

          let first = _.first(items);
          let rest = _.rest(items);
          let last = first;

          while (rest.indexOf(last + 1) != -1) {
            rest = _.without(rest, last + 1);
            last = last + 1;
          }
          sequence.push([first, last]);
          return find_sequences([sequence, rest]);
        };

        find_sequences([sequences, working_days]);

        let regions = _.map(sequences, function(sequence) {
          return {
            axis: "x",
            start: sequence[0] - 0.5,
            end: sequence[1] + 0.5,
            class: "workingday"
          };
        });

        let columns = [
          x,
          max,
          min,
          mean,
        ];

        if(pef[1]){
          columns.push(pef)
        }
        let getColStartWidths = function(){
          /*
          * Returns a list of objects of {start, width}
          */

         let lines  = d3.select(element).selectAll(".c3-xgrid-line line")[0].map(line=> {
            return {
              start: line.x1.baseVal.value,
            }
          });

          let cols = d3.select(element).selectAll(".c3-event-rect")[0]

          // by mapping to column we start with the first linw
          lines[0].start = cols[0].x.baseVal.value,

          lines.forEach((line, idx) => {
            if(idx+1 !== lines.length){
              line.width = lines[idx + 1].start - line.start
            }
          })

          let lastLine = _.last(lines);
          let lastColumn = _.last(cols);
          lastLine.width = lastColumn.width.baseVal.value

          return lines;
        };

        let prepend = function(parent, tagName){
          let tag = parent.append(tagName);
          let tagNode = tag.node();
          tagNode.parentNode.insertBefore(tagNode, tagNode.parentNode.firstChild);
          return tag;
        }

        let addTopLayer = function(){
          /*
          * Adds a top layer above the graph, removes it, if it exists
          */
          let firstG = d3.select(d3.select(element).selectAll("g")[0][0]);
          firstG.selectAll(".treatmentLayer").remove();
          let topLayer = prepend(firstG, "g");
          topLayer.classed("treatmentLayer", true);
          return topLayer;
        };

        let getYAxisEnd = function(){
          let e = d3.select(element).selectAll(".c3-axis-y .tick text")[0][0];
          return e.x.baseVal[0].value;
        }

        let addRow = function(parent, idx, ytext, cls){
            let cols = getColStartWidths();
            let textStart = getYAxisEnd()
            let section = parent.append("g");
            section.attr("transform", "translate(0, " +  (-25 * idx) + ")");
            // extends the line of the y axis
            let axis = section.append("line");
            axis.attr("x1", 0);
            axis.attr("x2", 0);
            axis.attr("y1", 0);
            axis.attr("y2", -30);
            axis.attr("stroke-width", "1");

            // the tick on the y axis
            let horizontalTick1 = section.append("line");
            horizontalTick1.attr("x1", -6);
            horizontalTick1.attr("x2", 0);
            horizontalTick1.attr("y1", -25);
            horizontalTick1.attr("y2", -25);

            let text = prepend(section, "text");
            text.attr("x", textStart);
            text.attr("y", "-8");
            text.attr("text-anchor", "end");
            text.classed(cls, true);
            let threshold = 15;
            let titleText = ytext;
            if(ytext && ytext.length > threshold){
              ytext = ytext.substr(0, threshold).concat("...");
            }
            text.text(ytext);

            let title = section.append("title");
            title.text(titleText);

            // extend all of the other columns up accordingly
            cols.forEach((col, idx) =>{
              if(idx === cols.length-1){
                return;
              }
              let colLine = section.append("line");
              colLine.attr("x1", col.start + col.width);
              colLine.attr("x2", col.start + col.width);
              colLine.attr("y1", -3);
              colLine.attr("y2", -30);
              colLine.attr("stroke-dasharray", "3");
              colLine.attr("z-index", 20);
              colLine.classed("treatment-dash-lines", true);
            });

            return section
        }

        let addTreatments = function(){
          /*
          * treatments come from the server are started/ended via trial num
          * so we translate that to column num
          */
          let cols = getColStartWidths();
          let topLayer = addTopLayer();
          Object.keys(data.treatments).forEach((treatmentName, treatmentIdx) => {

            let cls = "treatment-" + treatmentIdx % 3;
            let treatmentSection = addRow(topLayer, treatmentIdx, treatmentName, cls);

            data.treatments[treatmentName].forEach(treatmentObj => {

              // we bring through treatment with start and stop
              // as the treatment days so we need to translate
              // it to arra  index
              let columns = cols.slice(treatmentObj.start - 1, treatmentObj.end );
              let x1 = columns[0].start;
              let width = columns.reduce((accumulator, column) => {
                return accumulator + column.width;
              }, 0);

              let line = prepend(treatmentSection, "line");
              line.attr("x1", x1);
              line.attr("x2", x1 + width);
              line.attr("y1", "-12");
              line.attr("y2", "-12");

              line.attr("stroke-width", "14");
              line.classed(cls, true);
            });
          });

          let variabilityRow = addRow(topLayer, Object.keys(data.treatments).length, "% Variability", "");

          // add variance
          cols.forEach((col, idx) =>{
            let variability = data.days[idx].variabilty;

            if(!_.isUndefined(variability)){
              let g = prepend(variabilityRow, "g");
              g.attr("transform", "translate(" + col.start + ", -25)");
              let text = g.append("text");
              // text.attr("width", col.width).attr("height","15");
              text.attr("text-anchor", "middle").attr('alignment-baseline', 'middle');
              text.attr("x", col.width/2).attr("dy", ".82em").attr("dx", "0").classed("variance", true);
              text.classed("variability", true);
              text.text(variability);
              if(variability >= UPPER_BOUND){
                text.classed("upper-variability", true);
              }
            }
          });

          // // the default fill (0.1) opacity provided by d3 makes it so light you can't see
          // // workdays on the projector
          d3.select(element).selectAll(".c3-region.workingday rect").style("fill-opacity", "0.3");
        };

        let calculateGraphAxisAndHeight = function(columns){
          /*
          * The users would like to be able to compare graphs
          * between different patients.
          *
          * This is a difficult problem as peak flows cover
          * a different range of values (y axis) and
          * a varied number of days (x axis)
          *
          * The solution for the y axis is to account
          * for the vast majority of patients. We grow the axis
          * for when they are above the usual min max so the axis
          * are always the same but the graph grows to account for
          * extremes.
          *
          * The solution for the x axis is to keep the length
          * of a day on the x axis as a fixed amound, only when a patient
          * has a significant number of days (> 31) we will start squishing
          * it to make sure it fits on the page. (although it will horizontally
          * scroll on small screens)
          */

          // defaut mix max vaues
          let min = 300;
          let max = 650;

          // look at the values actually to be rendered
          // and adjust the min/maxes accordingly.
          columns = columns.filter(column=> column[0] !== 'x');
          let values = columns.flat();
          values = values.filter(value => !_.isString(value) && !_.isUndefined(value) && !_.isNull(value));
          let minInVaues = Math.min(...values);
          let maxInValues = Math.max(...values);

          if(minInVaues < min){
            min = Math.floor(minInVaues/50) * 50
          }

          if(maxInValues > max){
            max = (Math.floor(maxInValues/50) + 1) * 50
          }

          // the range is the min -50 and the max + 50
          let range = _.range(min, max+50, 50);
          let height = (max - min) * 2

          let args = {
            size: {
              height: height
            },
            axis: {
              max: max,
              min: min,
              tick: {
               values: range
             }
            }
          }

          if(columns[0].length < 32){
            let colWidth = element.parent().parent().width()/32
            args.size.width = (columns[0].length -1) * colWidth;
          }

          return args;
        }

        let calculatePadding = function(treatments){
          // padding at the top is 25 for each treatment + and additional 25 for variance
          let paddingTop = (Object.keys(treatments).length * 25) + 25;
          return {
            bottom: 30,
            left: 100,
            top: paddingTop,
          }
        }

        let getTooltip = function(d, CLASS){
          let trialNum = d[0].x;
          let day = data.days.find(day => day.day_num === trialNum)
          let rowTemplate = function(id, name, value){
            if(!value){
              value = "Unknown";
            }
            return `<tr class="${CLASS.tooltipName}-${id}">
            <td class="name">${name}</td><td class="value">${value}</td>
            </tr>
            `
          }

          let rows = d.map(row =>rowTemplate(row.id, row.name, row.value));
          rows.push(rowTemplate("variabilty", "Variabilty", day.variabilty));
          let dt = displayDateFilter(day.date);
          let dtStr;
          if(dt){
            dtStr = ` (${dt})`;
          }
          else{
            dtStr = ""
          }
          if(day.work_day){
            rows.push(`<tr class="${CLASS.tooltipName}-workday"><td class="text-center" colspan="2">Work day</td></tr>`)
          }

          return `
            <table class="${CLASS.tooltip}">
              <tr><th colspan='2'>Day ${trialNum} ${dtStr}</th></tr>
              ${rows.join("")}
            </table>
          `
        }

        let axisDimensions = calculateGraphAxisAndHeight(columns);

        let colorsOptions = [
          "#A6143B", "#D9628D", "#283959", "#C7A368"
        ]

        let colors = {}

        columns.forEach((column, idx) => {
          colors[column[0]] = colorsOptions[idx];
        });
        let ret = c3.generate({
          bindto: element[0],
          size: axisDimensions.size,
          padding: calculatePadding(data.treatments),
          data: {
            x: "x",
            columns: columns,
            colors: colors
          },
          axis: {
            x: {
              type: "indexed",
              tick: {
                fit: true,
                values: _.rest(x)
              },
              label: {
                text: "Trial day",
                position: 'outer-center'
              }
            },
            y: axisDimensions.axis
          },
          legend: {
            position: 'right'
          },
          grid: {
            x: {
              lines: gridLines
            },
            y: {
              show: true,
            }
          },
          point: {
            show: false
          },
          regions: regions,
          tooltip: {
            contents: function (d, defaultTitleFormat, defaultValueFormat, color) {
              let CLASS = this.CLASS;
              return getTooltip(d, CLASS);
            }
          },
          onrendered: function() {
            setTimeout(function(){ // timeout is needed for initial render.
              addTreatments();
            }, 0);
          }
        });
        scope.$watch('highlights.day_num', function(){
          if(scope.highlights){
            if(scope.highlights.day_num){
              ret.tooltip.show({x: scope.highlights.day_num});
            }
            else{
              ret.tooltip.hide({x: scope.highlights.day_num});
            }
          }
        });
      }
      $timeout(render_chart, 500);
    }
  };
});

directives.directive("reemit", function($parse, $timeout) {
  "use strict";
  /*
  * the angular js select2 wrapper does not accept dynamic event
  * names.
  *
  * Given we have n select2s on the peak flow form we need to
  * be able to broadcast an event and have it picked up
  * and translated to a local event name.
  *
  * e.g. if we need to focus on the first select 2
  * the peak flow form emits reset0 which is picked up
  * by the below directive and the                            n rebroadcast as
  * refocus to the correct select2 input.
  */
  return {
    scope: false,
    link: function(scope, element, attrs) {
      let ev = $parse(attrs.reemit)(scope);
      scope.$on(ev, function() {
        scope.$broadcast("refocus")
      });
    }
  };
});
