directives.directive("peakFlowGraph", function($timeout, PeakFlowGraphDataLoader) {
  "use strict";

  return {
    scope: {
      trialNum: "=",
      episodeId: "="
    },
    link: function(scope, element, attrs) {

      // make sure we don't call it too many times during the render
      var render_chart = _.once(function() {
        PeakFlowGraphDataLoader.load(scope.episodeId, scope.trialNum).then(function(data){
          var days = data.days;
          var x = ["x"].concat(_.compact(_.pluck(days, "day_num")));
          var mean = ["Mean"].concat(_.compact(_.pluck(days, "mean_flow")));
          var max = ["Max"].concat(_.compact(_.pluck(days, "max_flow")));
          var min = ["Min"].concat(_.compact(_.pluck(days, "min_flow")));

        // We want to colour days when the person was at work to easily identify them
        // It's _occupational_ lung disease after all.
        var working_days = _.map(
          _.filter(days, function(day) {
            return day.work_start || day.work_end;
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
          mean //, predicted
        ];

        var addVariance = function(){
          var d3Element = d3.select(element);
          var variabilties = _.pluck(data.days, "variabilty").filter(variabilty => !_.isUndefined(variabilty));
          var g = d3Element.selectAll('.c3-axis-x .tick').data(variabilties).append("g");
          g.attr("transform", "translate(-15, 20)");

          var rect = g.append("rect");
          rect.attr("width", "30").attr("height", "15");
          rect.style("fill", "white");
          rect.style("stroke", "red");
          rect.style("stroke-width", "2");

          var text = g.append("text");
          text.attr("width", "30").attr("height","15").classed("variance", true);
          text.attr("text-anchor", "middle").attr('alignment-baseline', 'middle');
          text.attr("x", "15").attr("dy", ".91em").attr("dx", "0").classed("variance", true);
          text.text(function(variabilty){
            return variabilty;
          });
        };

        var ret = c3.generate({
          bindto: element[0],
          padding: {
            bottom: 30
          },
          data: {
            x: "x",
            columns: columns
          },
          axis: {
            x: {
              type: "indexed",
              tick: {
                fit: true,
                values: _.rest(x)
              },
              label: "Days"
            }
          },
          legend: {
            position: 'right'
          },
          grid: {
            x: {
              lines: gridLines
            },
            y: { show: true }
          },
          regions: regions,
          onrendered: function() {
            setTimeout(function(){ // timeout is needed for initial render.
              addVariance()
            }, 0);
          }
        });
      })
      });
      $timeout(render_chart, 500);
    }
  };
});
