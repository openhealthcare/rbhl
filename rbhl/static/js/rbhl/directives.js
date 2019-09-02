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
            return day.work_start || day.work_end;
          }),
          function(day) {
            return day.day_num;
          }
        );

        working_days.sort(function(a, b) {
          return a - b;
        });

        var calculateTreatments = function(days){
          /*
          * if a treatment only appears for a single day,
          * we just state the name of the treament
          * otherwise we return e.g. aspirin starts
          * then aspirin finishes
          */
          var trialDayToTreatment = {}

          _.each(days, function(day){
            if(day.treatment_taken){
              trialDayToTreatment[day.trial_num] = day.treatment_taken;
            }
          });

          var trialDaysWithTreatments = _.keys(trialDayToTreatment);

          var result = {}

          _.each(trialDaysWithTreatments, function(day, idx){
            if(trialDaysWithTreatments.length === 1){
              result[day] = trialDayToTreatment[day];
            }
            else{
              var firstDay = null;
              var lastDay = null;

              if(idx !== 0){
                if(day + 1 !== trialDaysWithTreatments[idx + 1]){
                  lastDay = true;
                }
              }
              if(idx !== trialDaysWithTreatments.length-1){
                if(day -1 !== trialDaysWithTreatments[idx - 1]){
                  firstDay = true;
                }
              }
              if(firstDay && lastDay){
                result[day] = trialDayToTreatment[day];
              }
              else if(firstDay){
                result[day] = trialDayToTreatment[day] + " started";
              }
              else if(lastDay){
                result[day] = trialDayToTreatment[day] + " stopped";
              }
            }
          });

          return result;
        }

        var calculateNotes = function(days){
          /*
          * Notes appear as lines on the y access
          * if a treatment only appears for a single day
          * it is marked as as note, other wise it just
          * states the name of the drug
          */
          var result = {};

          _.each(days, function(day){
            if(day.note){
              result[day.trial_num] = day.notes;
            }
          });

          return result;
        }

        var calculateNotesAndTreatmentLines = function(days){
          /*
          * Returns the lines that we draw for treatments
          * and notes
          */
          var treatmentDays = calculateTreatments(days);
          var notesDays = calculateNotes(days);
          var allDays = _.uniq(_.keys(treatmentDays) + _.keys(notesDays));
          var result = [];
          _.each(allDays, function(day){
            var text = notesDays[day];
            if(treatmentDays[day]){
              if(text){
                text = text + ", " + treatmentDays[day];
              }
              else{
                text = treatmentDays[day];
              }
            }
            result.push({
              value: parseInt(day),
              text: text,
              class: "c3-note"
            });
          });

          return result;
        }

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
              class: "c3-dashed-line",
            };
          });
        };

        var calculateLines = function(x, days){
          var gridLines = calculateGridLines(x);
          var notesAndTreatments = calculateNotesAndTreatmentLines(days);
          var allLines = _.sortBy(gridLines.concat(notesAndTreatments), function(line){
            return line.value;
          });

          return allLines;
        }

        var lines = calculateLines(x, days);

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
              lines: lines
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
