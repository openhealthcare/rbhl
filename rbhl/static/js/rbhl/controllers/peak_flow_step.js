angular.module('opal.controllers').controller('PeakFlowStep',
  function(scope, step, episode, $location, $window) {
    "use strict";

    // list of time options that we can set for a flow time
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
    ];

    // a peak flow time, ie one of a list of times attatched to a day
    class PeakFlowTime {
      constructor(time, flow){
        this.time = time;
        this.flow = flow;
      }

      fieldString(){
        return "flow_" + this.time.replace(":", "")
      }
    }

    // models a peak flow day
    class PeakFlowDay {
      constructor(date, day_num){
        this.id = undefined;
        this.treatment_taken = undefined;
        this.note = undefined;
        this.work_day = false;
        this.trial_num = $location.search().trial_num;
        this.peakFlowTimes = [];
        this.date = date;
        this.day_num = day_num;
        this.form = {
          flow: undefined,
          time: undefined
        }
      }

      addFlow(idx){
        if(!this.form.time || !this.form.flow){
          return;
        }
        this.peakFlowTimes = _.filter(this.peakFlowTimes, (oldPft) => {
          return oldPft.time !== this.form.time;
        }, this);
        this.peakFlowTimes.push(new PeakFlowTime(this.form.time, this.form.flow));
        this.peakFlowTimes = _.sortBy(this.peakFlowTimes, pfg => {
          return scope.timeOptions.indexOf(pfg.time);
        });
        this.form.time = null;
        this.form.flow = null;
        scope.$broadcast("reset" + idx);
      }

      removeFlow(idx){
        this.peakFlowTimes.splice(idx, 1);
      }

      toDict(){
        var fields = [
          "treatment_taken",
          "note",
          "work_day",
          "trial_num",
          "date",
          "day_num",
        ];
        var json = {};

        _.each(fields, field=>{
          json[field] = this[field];
        }, this);

        _.each(this.peakFlowTimes, pft => {
          json[pft.fieldString()] = pft.flow;
        });

        return json;
      }
    }

    scope.initialise = function(){
      // We expect a get parameter of trial_num
      // which we use to handle the cop
      if(!$location.search().trial_num){
        $window.location.href = '/404';
        return;
      }

      scope.trialNum = $location.search().trial_num
      scope.editing.peak_flow_day = _.where(
        scope.editing.peak_flow_day,
        {trial_num: scope.editing.trial_num}
      )

      scope.editing.peak_flow_day = _.sortBy(scope.editing.peak_flow_day, "trial_num")
      // The number of trial days to show, usually this is
      // we pull this off the model if its populated
      if(scope.editing.peak_flow_day.length){
        scope.numOfTrials = _.max(scope.editing.peak_flow_day, x => {
          return x.trial_num;
        })
      }
      else{
        scope.numOfTrials = 0;
      }

      // when does the trial start
      if(scope.editing.peak_flow_day.length){
        scope.startDate = _.min(scope.editing.peak_flow_day, x => {
          return x.date;
        })
      }

      // just for test practices
      scope.startDate = new Date();
      scope.numOfTrials = 10;
      this.updateTrialNumbers();
    }


    scope.getTrialDays = function(numOfTrials, startDate){
      /*
      * Returns an array of PeakFlowDay
      *
      * e.g. if given a number of trials of 5 and a date of 1 April
      * it will return 1 April, 2 April, 3 April, 4 April, 5 April
      */
      if(!numOfTrials || !startDate){
        return [];
      }
      var range = _.range(numOfTrials);
      return  _.map(range, function(x){
        var dt = moment(startDate).add(x, "d")
        return new PeakFlowDay(dt, x+1)
      });
    }

    scope.updateTrialNumbers = function(){
      /*
      * Sets an array of dates that the trial covers
      */
      this.trialDays = this.getTrialDays(scope.numOfTrials, scope.startDate);
    }

    scope.getTrialInputs = someDate => {
      /*
      * Get's the trials inputs for a specific trial number
      */
      var trialNum = this.trialDays.indexOf(someDate);
      return _.where(scope.editing.peak_flow_day, {trial_num: trialNum});
    }

    scope.preSave = function(editing){
      editing.trial_num = $location.search().trial_num;
      editing.peak_flow_day = _.map(scope.trialDays, (td) => {
        return td.toDict();
      });
      return editing;
    }

    scope.initialise();
});
