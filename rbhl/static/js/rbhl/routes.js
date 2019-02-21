var app = angular.module('opal');
app.controller('WelcomeCtrl', function(){});

app.config(
    ['$routeProvider',
     function($routeProvider){
         //	     $routeProvider.when('/',  {redirectTo: '/list'})

         $routeProvider.when('/',  {
             controller: 'WelcomeCtrl',
             templateUrl: '/templates/welcome.html'}
                            )
             .when('/import',
                   {
                       controller: 'WelcomeCtrl',
                       templateUrl: '/templates/import.html'
                   })

     }]);

app.filter("toTime", function(){
    return function(x){
        if(!x){
            return ""
        }
        var str_x = String(x);
        if(!str_x.length){
            return ""
        }
        str_x.splice(str_x.length-2, 0, ":")
        return str_x
    }
})




app.directive('editPeakFlow', function($q, $timeout){
    "use strict";

    return {
      scope: false,
      link: function(scope, element, attrs){
        scope.times = [
            "06:00",
            "07:00",
            "08:00",
            "09:00",
            "10:00",
            "11:00",
            "12:00",
            "13:00",
            "14:00",
            "15:00",
            "16:00",
            "17:00",
            "18:00",
            "19:00",
            "20:00",
            "21:00",
            "22:00",
            "23:00",
        ]

        scope.fields = [
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
            "flow_2300",
        ]

        scope.selectedDayId = null;
        scope.selectedTime = null;
        scope.oldValue = null;
        scope.savingPromise = $q.defer().promise;

        scope.getFieldName = function(index){
            return scope.fields[index]
        }

        scope.openEditItem = function(day){
            var idx = scope.episode.peak_flow_day.indexOf(day);
            scope.episode.recordEditor.editItem('peak_flow_day', idx);
        }

        scope.edit = function(day, fieldName, time, $event){
            scope.selectedDayId = day.id;
            scope.selectedTime = time;
            scope.oldValue = day[fieldName];
            $timeout(function(){
                var target = $event.target;
                var a = $($(target.parentNode).find("input").get())
                a.focus();
            }, 1);
        }

        scope.addDay = function(){
           var maxNum = _.max(_.pluck(scope.episode.peak_flow_day, "day_num"))
           var pfd = scope.episode.newItem("peak_flow_day");
           var copy = pfd.makeCopy()
           _.each(scope.fields, function(field){
            copy[field] = 0;
           });
           copy.day_num = maxNum + 1;
           pfd.save(copy);
        };


        scope.save = function(selectedDayId, selectedTime, newValue){
            var deferred = $q.defer();
            var item = _.findWhere(scope.episode.peak_flow_day, {id: selectedDayId});
            var copy = item.makeCopy();
            copy[scope.fields[scope.times.indexOf(selectedTime)]] = newValue;
            item.save(copy).then(function(x){
                scope.$broadcast("reloadGraph")
                deferred.resolve(x);
            });
            return deferred.promise
        }

        scope.loseFocus = function(value){
            if(value !== scope.oldValue){
                var saving = scope.save(scope.selectedDayId, scope.selectedTime, value);
                // we save synchronously to make sure we are up to date.
                // with consistency tokens and previous results.
                scope.savingPromise = scope.savingPromise.then(saving);
            }
            scope.selectedDayId = null;
            scope.selectedTime = null;
            scope.oldValue = null;
        }

        scope.isSelected = function(dayId, time){
            return dayId === scope.selectedDayId && scope.selectedTime === time
        }

        // they don't have to lose focus, they can
        // press the enter key
        scope.onEnter = function(keyEvent, value) {
            if(keyEvent.which === 13){
                scope.loseFocus(value)
            }
        }
      }
    }
});

app.directive('peakFlowGraph', function($timeout){
    return function(scope, element, attrs){
        function render_chart(){
            var fields = [
                'flow_0600','flow_0700','flow_0800','flow_0900','flow_1000','flow_1100',
                'flow_1200','flow_1300','flow_1400','flow_1500','flow_1600','flow_1700',
                'flow_1800','flow_1900','flow_2000','flow_2100','flow_2200','flow_2300',
            ]
            var days = scope.episode.peak_flow_day;
            days = _.filter(days, function(day){ return day.trial_num == 1 });
            var x  = ['x']
            var mean = ['Mean']
            var max = ['Max']
            var min = ['Min']
            var pef = ["PEF"]
            var pefValue = scope.episode.peak_expiratory_flow[0].value
            // var predicted = ['Predicted Mean']
            _.each(days, function(day){
                var count = 0
                var sum = 0
                var values = []
                _.each(fields, function(field){
                    if(day[field]){
                        values.push(day[field])
                        count += 1;
                        sum += day[field];
                    }
                });
                if(count){
                    x.push(day.day_num);
                    mean.push(parseInt(sum/count));
                    max.push(_.max(values));
                    min.push(_.min(values));
                    pef.push(pefValue);
                    // predicted.push(510);
                }
            });

            // We want to colour days when the person was at work to easily identify them
            // It's _occupational_ lung disease after all.

            var working_days = _.map(
                _.filter(days, function(day){ return day.work_start || day.work_end }),
                function(day){ return day.day_num }
            );

            working_days.sort(function(a, b){return a-b});

            var sequences = []

            var find_sequences = function(data){
                var sequence = data[0], items = data[1];

                if(items.length == 0){ return }

                var first = _.first(items), rest = _.rest(items);
                var last = first;

                while(rest.indexOf(last+1) != -1){
                    rest = _.without(rest, last+1);
                    last = last +1;
                }
                sequence.push([first, last])
                return find_sequences([sequence, rest])
            }

            find_sequences([sequences, working_days])


            var regions = _.map(sequences, function(sequence){
                return {axis: 'x', start: sequence[0], end: sequence[1], class: 'workingday'}
            });

            var columns = [
                x, max, min, mean, pef
            ]
            var ret = c3.generate({
                bindto: element[0],
                data: {
                    x:'x',
                    columns: columns
                },
                axis: {
                    x: {
                        type: 'indexed',
                        tick: {
                            fit: true,
                            values: _.rest(x),
                            format: function (x) { return 'Day ' + x; }
                        },
                        label: 'Days',
                    }
                },
                grid: {
                    x: {show: true},
                    y: {show: true}
                },
                regions: regions

            });
        }
        $timeout(render_chart, 500);

        // when anything has changed in the table below
        // reload the graph
        scope.$on("reloadGraph", function(){
            render_chart()
        });
    }
})
