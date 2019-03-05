angular.module('opal.controllers').controller('PeakFlowStep',
  function(scope, step, episode, $location, $window) {
    "use strict";

    scope.initialise = function(){
      // We expect a get parameter of trial_num
      // which we use to handle the cop
      if(!$location.search().trial_num){
        $window.location.href = '/404';
        return;
      }

      scope.editing.trial_num = $location.search().trial_num
      scope.editing.peak_flow_day = _.where(
        scope.editing.peak_flow_day,
        {trial_num: scope.editing.trial_num}
      )


      scope.editing.peak_flow_day = _.sortBy(scope.editing.peak_flow_day, "trial_num")
      // The number of trial days to show, usually this is
      // we pull this off the model if its populated
      if(scope.editing.peak_flow_day.length){
        scope.numOfTrials = _.max(scope.editing.peak_flow_day, function(x){
          return x.trial_num;
        })
      }
      else{
        scope.numOfTrials = 0;
      }

      // when does the trial start
      if(scope.editing.peak_flow_day.length){
        scope.startDate = _.min(scope.editing.peak_flow_day, function(x){
          return x.date;
        })
      }

      // just for test practices
      scope.startDate = new Date();
      scope.numOfTrials = 10;

      scope.timeOptions = [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
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

      /*
      * all the different day inputs are stored on a form object
      * with an incrementing
      */
      scope.form = {};
      scope.results = {};

      this.updateTrialNumbers();
    }



    scope.getTrialDays = function(numOfTrials, startDate){
      /*
      * Returns the array of dates that the trial data covers
      *
      * e.g. if given a number of trials of 5 and a date of 1 April
      * it will return 1 April, 2 April, 3 April, 4 April, 5 April
      */
      if(!numOfTrials || !startDate){
        return [];
      }
      var range = _.range(numOfTrials);
      var a =  _.map(range, function(x){
        return moment(startDate).add(x, "d")
      });
      return a;
    }

    scope.updateTrialNumbers = function(){
      /*
      * Sets an array of dates that the trial covers
      */
      this.trialDays = this.getTrialDays(scope.numOfTrials, scope.startDate);
    }

    scope.getTrialInputs = function(someDate){
      /*
      * Get's the trials inputs for a specific trial number
      */
      var trialNum = this.trialDays.indexOf(someDate);
      return _.where(scope.editing.peak_flow_day, {trial_num: trialNum});
    }

    scope.addFlow = function(idx){
      /*
      * Adds an editing property based on the form
      */
      if(!scope.results[idx]){
        scope.results[idx] = [];
      }
      scope.results[idx].push(_.clone(scope.form[idx]));
      _.each(scope.form, function(v, k){
        scope.form[k] = undefined;
      });
      scope.$broadcast("reset" + idx);
    }

    scope.initialise();
});
