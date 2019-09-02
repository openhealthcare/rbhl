directives.directive("peakFlowGraph", function($timeout) {
  "use strict";
  return {
    scope: {
      days: "="
    },
    link: function(scope, element, attrs) {
      function render_chart() {
        var fields = [
          "flow_0600",
          "flow_0700",
          "flow_0800",
          "flow_0900",
          "flow_1000",
          "flow_1100",
          "flow_1200",
          "flow_1300",
          "flow_1400",
          "flow_1500",
          "flow_1600",
          "flow_1700",
          "flow_1800",
          "flow_1900",
          "flow_2000",
          "flow_2100",
          "flow_2200",
          "flow_2300"
        ];
        // var days = scope.episode.peak_flow_day;
        // var days = _.filter(scope.days, function (day) { return day.trial_num == 1 });
        var days = scope.days;
        var x = ["x"];
        var mean = ["Mean"];
        var max = ["Max"];
        var min = ["Min"];
        // var predicted = ['Predicted Mean']
        _.each(days, function(day) {
          var count = 0;
          var sum = 0;
          var values = [];
          _.each(fields, function(field) {
            if (day[field]) {
              values.push(day[field]);
              count += 1;
              sum += day[field];
            }
          });
          if (count) {
            x.push(day.day_num);
            mean.push(parseInt(sum / count));
            max.push(_.max(values));
            min.push(_.min(values));
            // predicted.push(510);
          }
        });

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
          mean //, predicted
        ];
        var ret = c3.generate({
          bindto: element[0],
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
          grid: {
            x: {
              lines: gridLines
            },
            y: { show: true }
          },
          regions: regions
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
  * by the below directive and then rebroadcast as
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
