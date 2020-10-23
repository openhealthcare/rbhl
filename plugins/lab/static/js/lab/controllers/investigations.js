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

    allDates = allDates.concat(_.pluck($scope.episode.blood_book, "blood_date"));

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
    var tests;
    if(testType == "blood_book"){
      var bb_tests = _.filter($scope.episode[testType], function(test){
        return displayDateFilter(test.blood_date) === dateKey;
      });
      tests = _.sortBy(bb_tests, function(x){return x.allergen});
    }
    else{
      tests = _.filter($scope.episode[testType], function(test){
        return displayDateFilter(test.date) === dateKey;
      });

      if(tests.length){
        if(testType === 'skin_prick_test'){
          return SkinPrickTestHelper.sortTests(tests);
        }
      }
    }
    return tests;
  }

  this.combineBloodBookResultResults = function(bloodBookResults){
    /*
    * The blood book result.result used to be a generic term for a
    * free text input of all lab test information.
    *
    * This means every result for a field with a 'result' value
    * is of type result, to stop a list of result result result
    * lets combine them all.
    */
    var allResults = _.pluck(bloodBookResults, "result");
    return _.filter(allResults, function(i){
      return i && i.length
    }).sort();
  }

  this.isAtopic = function(skinPrickTests){
    return SkinPrickTestHelper.isAtopic(skinPrickTests);
  }
});