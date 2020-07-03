angular.module('opal.controllers').controller('InvestigationsView', function($scope, displayDateFilter, SkinPrickTestHelper) {
  "use strict";

  // Bloodbook obervation names
  var RESULT = "Result"
  var ALLERGEN = "Allergen"
  var ANTIGEN_NO = "Antigen #"
  var KUL = "KU/L"
  var CLASS = "Class"
  var RAST = "RAST %B"
  var PRECIPITIN = "Precipitin"
  var IGG = "mg/L"

  this.getTestDateKeys = function(){
    /*
    * Returns a list of strings of dates ordered in descending order
    */
    var allDates = []
    _.each(["spirometry", "skin_prick_test", "bronchial_test", "other_investigations"], function(key){
      allDates = allDates.concat(_.pluck($scope.episode[key], 'date'));
    });

    _.each($scope.episode.specimen, function(s){
      allDates.push(s.blood_date);
    });

    allDates = _.sortBy(allDates,function(someDate){
      if(!someDate){
        return 0;
      }
      return someDate.valueOf();
    });
    allDates = allDates.reverse()
    return _.uniq(_.map(allDates, function(d){ return displayDateFilter(d)}));
  }

  this.getTestsForDateKey = function(testType, dateKey){
    /*
    * for a given date key string and test type returns
    * all tests for that day.
    */
    var dateField = "date";
    if(testType === 'specimen'){
      dateField = 'blood_date'
    }
    var tests = _.filter($scope.episode[testType], function(test){
      return displayDateFilter(test[dateField]) === dateKey;
    });

    if(tests.length){
      if(testType === 'skin_prick_test'){
        return SkinPrickTestHelper.sortTests(tests);
      }
    }

    return tests;
  }

  this.isAtopic = function(skinPrickTests){
    return SkinPrickTestHelper.isAtopic(skinPrickTests);
  }

  this.labTestObsToObj = function(observationArray){
    var result = {};
    _.each(observationArray, function(obs){
      result[obs.observation_name] = obs.observation_value
    });
    return result;
  }

  this.getTestDisplay = function(observationArray){
    var labTestObj = this.labTestObsToObj(observationArray);
    var label = "";
    var value = [];

    if(labTestObj[ALLERGEN] && labTestObj[ALLERGEN].length){
      label = labTestObj[ALLERGEN];

      if(labTestObj[ANTIGEN_NO]){
        label = label + " (" + labTestObj[ANTIGEN_NO] + ")";
      }

      if(labTestObj[KUL]){
        value.push(labTestObj[KUL] + " kU/L");
      }

      if(labTestObj[CLASS]){
        value.push(labTestObj[CLASS] + " CLASS");
      }

      if(labTestObj[RAST]){
        var rast = labTestObj[RAST].substring(0, 5);
        rast = Math.round(parseFloat(rast), 2);
        value.push(rast + " %B");
      }

      if(labTestObj[PRECIPITIN]){
        value.push(labTestObj[PRECIPITIN] + " mg/L");
      }
    }
    else if(labTestObj[RESULT] && labTestObj[RESULT].trim().length){
      var splitted = labTestObj[RESULT].trim().split(")");
      if(splitted.length > 1){
        label = splitted.shift() + ")"
        value.push(splitted.join(")"));
      }
      else{
        var splitted = labTestObj[RESULT].trim().split(" ", 1);
        if(splitted.length === 2){
          label = splitted.shift();
          value.push(splitted).join(" ");
        }
      }
    }
    return {
      label: label,
      value: value
    }
  }

  this.getAntigenNo = function(array){
    var title = "";
    var allergenNo = _.findWhere(array, {observation_name: "Antigen #"})
    if(result){
      return result.observation_value;
    }

  }

  this.sortBloodBookObs = function(array){
    var result = [];
    var observationNames = [
      "Result",
      "Allergen",
      "KU/L",
      "Class",
      "RAST %B",
      "Preciptin",
      "mg/L",
    ];

    _.each(observationNames, function(observationName){
      var resultWithField = _.filter(array, {observation_name: observationName});
      result = result.concat(resultWithField);
    });

    return result;
  };
});