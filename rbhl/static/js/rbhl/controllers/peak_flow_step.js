/*
* The peak flow step is a way if adding in information of a patients peak flows.
*
* The nurse enters a start date and number of days and it populates the days.
*
* Per day she types in a time presses tab to switch to the flow box
* then a flow then presses enter. The time/flow is added to the correct
* day and the focus is set back to the time field.
*/
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
      time = undefined;
      flow = undefined;

      constructor(time, flow){
        this.time = time;
        this.flow = flow;
      }
    }

    // models a peak flow day
    class PeakFlowDay {
      id = undefined;
      treatment_taken = undefined;
      note = undefined;
      work_day = undefined;
      trial_num = $location.search().trial_num;
      peakFlowTimes = [];
      date = null;
      day_num = null;

      // this is the data in the two inputs before you
      // add a new peak flow time.
      form = {
        flow: undefined,
        time: undefined
      }

      constructor(date, day_num){
        this.date = date;
        this.day_num = day_num;
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
          json[timeToField[pft.time]] = pft.flow;
        });

        return json;
      }

      static fromDict(json){
        var pfts = [];
        var keys = Object.keys(json);
        var pfd = new PeakFlowDay(json.date, json.day_num);
        _.each(keys, k => {
          if(k == "date" && k == "day_num"){
            return;
          }
          if(timeOptions[k]){
            if(json[k]){
              pfts.push(new PeakFlowTime(timeOptions[k], json[k]))
            }
            return
          }
          pfd[k] = json[k]
        });
        pfd.peakFlowTimes = pfts;
        return pfd;
      }
    }

    scope.initialise = function(){
      // We expect a get parameter of trial_num
      // which we use to handle the cop
      if(!$location.search().trial_num){
        $window.location.href = '/404';
        return;
      }
      scope.trialNum = parseInt($location.search().trial_num);
      this.setUpTrialNumbers();

      // The number of trial days to show
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


    scope.getTrialDays = function(numOfTrials, startDate, startDayNum){
      /*
      * Returns an array of PeakFlowDay
      *
      * e.g. if given a number of trials of 5 and a date of 1 April
      * it will return 1 April, 2 April, 3 April, 4 April, 5 April
      */
      var range = _.range(numOfTrials);
      return  _.map(range, function(x){
        var dt = moment(startDate).add(x, "d")
        return new PeakFlowDay(dt, x+startDayNum)
      });
    }

    scope.setUpTrialNumbers = function(){
      var existingPeakFlows = _.where(
        scope.editing.peak_flow_day,
        {trial_num: scope.trialNum}
      )

      if(existingPeakFlows.length){
        existingPeakFlows = _.sortBy(existingPeakFlows, "day_num")
        scope.trialDays = _.map(existingPeakFlows, epf => PeakFlowDay.fromDict(epf));
        scope.startDate = _.min(scope.trialDays, x => {
          return x.date;
        }).date;
        scope.numOfTrials = _.max(scope.trialDays, x => {
          return x.day_num;
        }).day_num;
      }
      else{
        scope.startDate = null;
        scope.trialDays = 0;
      }
    }

    scope.updateTrialNumbers = function(){
      /*
      * What happens when you update the form after its rendered
      */
      if(!scope.numOfTrials || !scope.startDate){
        return
      }

      if(!scope.trialDays.length){
        scope.trialDays = scope.getTrialDays(scope.numOfTrials, scope.startDate, 1);
      }

      if(scope.numOfTrials < scope.trialDays.length){
        scope.trialDays = scope.trialDays.slice(0, scope.numOfTrials);
      }
      else if(scope.numOfTrials > scope.trialDays.length){
        var numNewTrialDays = scope.numOfTrials - scope.trialDays.length;
        var existingMaxDate = _.max(scope.trialDays, x => {
          return x.date;
        }).date;
        var newStartDate = moment(existingMaxDate).add(1, "d")
        var newDayNum = _.max(scope.trialDays, x => {
          return x.day_num;
        }).day_num + 1;
        var newTrialDays = scope.getTrialDays(numNewTrialDays, newStartDate, newDayNum);
        scope.trialDays = scope.trialDays.concat(newTrialDays);
      }

      var minDate = _.min(scope.trialDays, x => {
        return x.date;
      }).date;

      if(scope.startDate !== minDate){
        _.each(scope.trialDays, td => {
          td.date = moment(scope.startDate).add(td.day_num - 1, "d");
        });
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
});
