angular.module('opal.controllers').controller('PeakFlowStep',
  function(scope, step, episode, $location, $window) {
    "use strict";

    // list of time options that we can set for a flow time
    var timeOptions = {
      flow_0000: "00:00",
      flow_0100: "01:00",
      flow_0200: "02:00",
      flow_0300: "03:00",
      flow_0400: "04:00",
      flow_0500: "05:00",
      flow_0600: "06:00",
      flow_0700: "07:00",
      flow_0800: "08:00",
      flow_0900: "09:00",
      flow_1000: "10:00",
      flow_1100: "11:00",
      flow_1200: "12:00",
      flow_1300: "13:00",
      flow_1400: "14:00",
      flow_1500: "15:00",
      flow_1600: "16:00",
      flow_1700: "17:00",
      flow_1800: "18:00",
      flow_1900: "19:00",
      flow_2000: "20:00",
      flow_2100: "21:00",
      flow_2200: "22:00",
      flow_2300: "23:00",
    }

    scope.timeOptions = Object.values(timeOptions);

    // a peak flow time, ie one of a list of times attatched to a day
    class PeakFlowTime {
      constructor(time, flow){
        this.time = time;
        this.flow = flow;
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

        var timeToField = _.invert(timeOptions);

        _.each(this.peakFlowTimes, pft => {
          json[timeToField[pft.flow]] = pft.flow;
        });

        return json;
      }
    }

    PeakFlowDay.fromDict = function(json){
      var pfts = [];
      var keys = Object.keys(json);
      var pfd = new PeakFlowDay(json.date, json.day_num);
      _.each(keys, k => {
        if(k == "date" && k == "day_num"){
          return;
        }
        if(timeOptions[k]){
          pfts.push(new PeakFlowTime(timeOptions[k], json[k]))
          return
        }
        pfd[k] = json[k]
      });
      pfd.peakFlowTimes = pfts;
      return pfd;
    }

    scope.initialise = function(){
      // We expect a get parameter of trial_num
      // which we use to handle the cop
      if(!$location.search().trial_num){
        $window.location.href = '/404';
        return;
      }
      scope.trialNum = parseInt($location.search().trial_num);
      this.updateTrialNumbers();

      // The number of trial days to show, usually this is
      // we pull this off the model if its populated
      if(scope.trialDays.length){
        scope.numOfTrials = _.max(scope.trialDays, x => {
          return x.day_num;
        }).day_num;
        scope.startDate = _.min(scope.trialDays, x => {
          return x.date;
        }).date;
      }
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
      var existingPeakFlows = _.where(
        scope.editing.peak_flow_day,
        {trial_num: scope.trialNum}
      )

      if(existingPeakFlows.length){
        existingPeakFlows = _.sortBy(existingPeakFlows, "day_num")
        this.trialDays = _.map(existingPeakFlows, epf => PeakFlowDay.fromDict(epf));
      }
      else{
        this.trialDays = this.getTrialDays(scope.numOfTrials, scope.startDate);
      }
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
    debugger;
});
