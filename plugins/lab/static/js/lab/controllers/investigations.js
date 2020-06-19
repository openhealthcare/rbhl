angular.module('opal.controllers').controller('InvestigationsView', function($scope, displayDateFilter, SkinPrickTestHelper) {
  "use strict";

  this.getTestDateKeys = function(){
    /*
    * Returns a list of strings of dates ordered in descending order
    */
    var allDates = []
    _.each(["spirometry", "skin_prick_test", "bronchial_test", "other_investigations"], function(key){
      allDates = allDates.concat(_.pluck($scope.episode[key], 'date'));
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
    var tests = _.filter($scope.episode[testType], function(test){
      return displayDateFilter(test.date) === dateKey;
    });

    if(tests.length){
      if(testType === 'skin_prick_test'){
        return SkinPrickTestHelper.sortTests(tests);
      }
    }

    return tests;
  }

  this.testCount = function(){
    /*
    * We display tests by date, so a straight count does not
    * not make sense, especially for skin prick tests
    * where they are done as a set. So lets just do a
    * count of distinct test type dates
    */
    var patient = $scope.patient;
    var count = patient.spirometry.length + patient.bronchial_test.length + patient.other_investigations.length;
    var count = 0;
    _.each(["spirometry", "bronchial_test", "skin_prick_tests", "other_investigations"], function(testType){
      // date equality in js is awkward, casting it to a date handles nulls and gives us date
      // rather than datetime equality
      var displayDates = _.map(patient[testType], function(someTest){ return displayDateFilter(someTest.date)})
      var distinctDates = _.uniq(displayDates);
      count += distinctDates.length;
    });
    return count;
  }

  this.isAtopic = function(skinPrickTests){
    return SkinPrickTestHelper.isAtopic(skinPrickTests);
  }
});