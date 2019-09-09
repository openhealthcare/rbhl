directives.directive("peakFlowGraph", function($timeout) {
  "use strict";

  return {
    scope: {
      data: "=",
      highlights: "="
    },
    link: function(scope, element, attrs) {
      var data = scope.data;

      // make sure we don't call it too many times during the render
      var render_chart = function() {
          var days = data.days;
          var x = ["x"].concat(_.compact(_.pluck(days, "day_num")));
          var mean = ["Mean"].concat(_.compact(_.pluck(days, "mean_flow")));
          var max = ["Max"].concat(_.compact(_.pluck(days, "max_flow")));
          var min = ["Min"].concat(_.compact(_.pluck(days, "min_flow")));
          var pef = ["PEF"].concat(_.compact(_.pluck(days, "pef_flow")));

          scope.completeness = data.completeness;
          scope.overrall_mean = data.overrall_mean;
          scope.pef_mean = data.pef_mean;

        // We want to colour days when the person was at work to easily identify them
        // It's _occupational_ lung disease after all.
        var working_days = _.map(
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

        var calculateGridLines = function(trialDays) {
          /*
           * the grid lines should be intra file day not
           * on the day itself
           */
          var gridLinesMax = _.max(trialDays);
          var gridLinesMin = _.min(trialDays);
          var range = _.range(gridLinesMin - 0.5, gridLinesMax + 0.5, 1);
          return _.map(range, function(r) {
            return {
              value: r,
              class: "c3-dashed-line"
            };
          });
        };

        var gridLines = calculateGridLines(x);
        var sequences = [];

        var find_sequences = function(data) {
          var sequence = data[0],
            items = data[1];

          if (items.length == 0) {
            return;
          }

          var first = _.first(items),
            rest = _.rest(items);
          var last = first;

          while (rest.indexOf(last + 1) != -1) {
            rest = _.without(rest, last + 1);
            last = last + 1;
          }
          sequence.push([first, last]);
          return find_sequences([sequence, rest]);
        };

        find_sequences([sequences, working_days]);

        var regions = _.map(sequences, function(sequence) {
          return {
            axis: "x",
            start: sequence[0] - 0.5,
            end: sequence[1] + 0.5,
            class: "workingday"
          };
        });

        var columns = [
          x,
          max,
          min,
          mean, //, predicted
          pef
        ];

        var getColStartWidths = function(){
          /*
          * Returns a list of objects of {start, width}
          */
          return d3.select(element).selectAll(".c3-event-rect")[0].map(col=> {
            return {
              start: col.x.baseVal.value,
              width: col.width.baseVal.value
            }
          });
        };

        var prepend = function(parent, tagName){
          var tag = parent.append(tagName);
          var tagNode = tag.node();
          tagNode.parentNode.insertBefore(tagNode, tagNode.parentNode.firstChild);
          return tag;
        }

        var addTopLayer = function(){
          /*
          * Adds a top layer above the graph, removes it, if it exists
          */
          var firstG = d3.select(d3.select(element).selectAll("g")[0][0]);
          firstG.selectAll(".treatmentLayer").remove();
          var topLayer = prepend(firstG, "g");
          topLayer.classed("treatmentLayer", true);
          return topLayer;
        };

        var getYAxisEnd = function(){
          var e = d3.select(element).selectAll(".c3-axis-y .tick text")[0][0];
          return e.x.baseVal[0].value;
        }

        // var getXAxisTickXPositions = function(){
        //   var ticks = d3.select(element).selectAll('.c3-axis-x .tick text');
        //   debugger;
        //   return ticks.map(t => t[0].x.baseValue);
        // }
        var addRow = function(parent, idx, ytext, cls){
            var cols = getColStartWidths();
            var textStart = getYAxisEnd()
            var section = parent.append("g");
            section.attr("transform", "translate(0, " +  (-25 * idx) + ")");
            // extends the line of the y axis
            var axis = section.append("line");
            axis.attr("x1", 0);
            axis.attr("x2", 0);
            axis.attr("y1", 0);
            axis.attr("y2", -30);
            axis.attr("stroke-width", "1");

            // the tick on the y axis
            var horizontalTick1 = section.append("line");
            horizontalTick1.attr("x1", -6);
            horizontalTick1.attr("x2", 0);
            horizontalTick1.attr("y1", -25);
            horizontalTick1.attr("y2", -25);

            var text = prepend(section, "text");
            text.attr("x", textStart);
            text.attr("y", "-8");
            text.attr("text-anchor", "end");
            text.classed(cls, true);
            text.text(ytext);

            // extend all of the other columns up accordingly
            cols.forEach(col =>{
              var colLine = section.append("line");
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

        var addTreatments = function(){
          /*
          * treatments come from the server are started/ended via trial num
          * so we translate that to column num
          */
          var cols = getColStartWidths();
          var topLayer = addTopLayer();
          Object.keys(data.treatments).forEach((treatmentName, treatmentIdx) => {

            var treatmentSection = addRow(topLayer, treatmentIdx, treatmentName, cls)
            var cls = "treatment-" + treatmentIdx % 3;

            data.treatments[treatmentName].forEach(treatmentObj => {

              // we bring through treatment with start and stop
              // as the treatment days so we need to translate
              // it to arra  index
              var columns = cols.slice(treatmentObj.start - 1, treatmentObj.end );
              var x1 = columns[0].start;
              var width = columns.reduce((accumulator, column) => {
                return accumulator + column.width;
              }, 0);

              var line = prepend(treatmentSection, "line");
              line.attr("x1", x1);
              line.attr("x2", x1 + width);
              line.attr("y1", "-12");
              line.attr("y2", "-12");
              line.attr("stroke-width", "14");
              line.classed(cls, true);
            });
          });

          var variabilityRow = addRow(topLayer, Object.keys(data.treatments).length, "% Variability", "variability");

          // add variance
          cols.forEach((col, idx) =>{
            var variability = data.days[idx].variabilty;

            if(!_.isUndefined(variability)){
              var g = prepend(variabilityRow, "g");
              g.attr("transform", "translate(" + col.start + ", -25)");
              var text = g.append("text");
              // text.attr("width", col.width).attr("height","15");
              text.attr("text-anchor", "middle").attr('alignment-baseline', 'middle');
              text.attr("x", col.width/2).attr("dy", ".82em").attr("dx", "0").classed("variance", true);
              text.classed("variability", true);
              text.text(variability);
            }
          });

          // the default fill (0.1) opacity provided by d3 makes it so light you can't see
          // workdays on the projector
          d3.select(element).selectAll(".c3-region.workingday rect").style("fill-opacity", "0.2");
        };

        var calculateGraphAxisAndHeight = function(columns){
          /*
          * Its been requested that the graphs have a fixed axis
          * however the range of values is quite large but often
          * the docs care about a small range.
          *
          * The solution to this is that we fix the axis to account
          * for the vast majority of patients. We grow the axis
          * for when they are above the usual min max so the axis
          * are always the same but the graph grows to account for
          * extremes.
          */

          // defaut mix max vaues
          var min = 300;
          var max = 750;

          // look at the values actually to be rendered
          // and adjust the min/maxes accordingly.
          columns = columns.filter(column=> column[0] !== 'x');
          var values = columns.flat();
          values = values.filter(value => !_.isString(value));
          var minInVaues = Math.min(...values);
          var maxInValues = Math.max(...values);

          if(minInVaues < min){
            min = Math.floor(minInVaues/50) * 50
          }

          if(maxInValues > max){
            max = (Math.floor(maxInValues/50) + 1) * 50
          }

          // the range is the min -50 and the max + 50
          var range = _.range(min, max+50, 50);
          var height = max - min;

          return {
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
        }

        var calculatePadding = function(treatments){
          // padding at the top is 25 for each treatment + and additional 25 for variance
          var paddingTop = (Object.keys(treatments).length * 25) + 25;
          return {
            bottom: 30,
            left: 100,
            top: paddingTop,
          }
        }

        var axisDimensions = calculateGraphAxisAndHeight(columns);

        var ret = c3.generate({
          bindto: element[0],
          size: axisDimensions.size,
          padding: calculatePadding(data.treatments),
          data: {
            x: "x",
            columns: columns,
          },
          axis: {
            x: {
              type: "indexed",
              tick: {
                fit: true,
                values: _.rest(x)
              },
              label: "Trial day"
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
          onrendered: function() {
            setTimeout(function(){ // timeout is needed for initial render.
              addTreatments();
            }, 0);
          }
        });
        scope.$watch('highlights.day_num', function(){
          if(scope.highlights){
            if(scope.highlights.day_num){
              ret.tooltip.show({x: scope.highlights.day_num-1});
            }
            else{
              ret.tooltip.hide({x: scope.highlights.day_num-1});
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
      var ev = $parse(attrs.reemit)(scope);
      scope.$on(ev, function() {
        scope.$broadcast("refocus")
      });
    }
  };
});
