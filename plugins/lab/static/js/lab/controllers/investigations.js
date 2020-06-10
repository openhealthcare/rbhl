angular.module('opal.controllers').controller('InvestigationsView', function($scope, displayDateFilter) {
  "use strict";

  var CONTROL_TESTS = [
    "Neg control",
    "Pos control",
  ]

  var STANDARD_TESTS = [
    "Asp. fumigatus",
    "Grass pollen",
    "Cat",
    "House dust mite"
  ]

  var ROUTINE_TEST_ORDER = CONTROL_TESTS.concat(STANDARD_TESTS);


  this.getTestDateKeys = function(){
    /*
    * Returns a list of strings of dates ordered in descending order
    */
    var allDates = []
    _.each(["spirometry", "skin_prick_test", "bronchial_test", "other_investigations"], function(key){
      allDates = allDates.concat(_.pluck($scope.episode[key], 'date'));
    });

    allDates.sort();
    allDates.reverse()
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
        return this.sortSkinPrickTests(tests);
      }
    }

    return tests;
  }

  this.isAtopic = function(skinPrickTests){
    /*
    * A patient is atopic if they have at least one
    * result of 3mm or more for a routine skin prick
    * test
    */
    var routineSpts = _.filter(skinPrickTests, function(spt){
      return _.contains(STANDARD_TESTS, spt.substance)
    });

    return !!_.filter(routineSpts, function(spt){
      return spt.wheal >= 3;
    }).length
  }

  this.sortSkinPrickTests = function(skinPrickTests){
    /*
    * Sorts skin prick tests so that the routine tests are
    * first done in the order above, which is the order they
    * are administered.
    *
    * Other tests are then in an alphabetical order.
    */
   var routineSkinPrickTests = [];
   var specificSkinPrickTests = [];
   _.each(skinPrickTests, function(spt){
     if(_.contains(ROUTINE_TEST_ORDER, spt.substance)){
      routineSkinPrickTests.push(spt);
     }
     else{
      specificSkinPrickTests.push(spt);
     }
   });

   routineSkinPrickTests = _.sortBy(routineSkinPrickTests, function(rspt){
    return ROUTINE_TEST_ORDER.indexOf(rspt.substance);
   });

   specificSkinPrickTests = _.sortBy(specificSkinPrickTests, 'substance');
   return routineSkinPrickTests.concat(specificSkinPrickTests);
  }
});