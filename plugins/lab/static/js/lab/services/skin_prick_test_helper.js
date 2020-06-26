angular.module('opal.services').factory('SkinPrickTestHelper', function() {
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

  var ROUTINE_TESTS = CONTROL_TESTS.concat(STANDARD_TESTS)

  var sortTests = function(skinPrickTests){
    /*
    * Sorts skin prick tests so that the routine tests are
    * first done in the order above, which is the order they
    * are administered.
    *
    * Other tests are then in an alphabetical order.
    */
    var routineTests = [];
    var specificSkinPrickTests = _.clone(skinPrickTests);

    _.each(ROUTINE_TESTS, function(rto){
      var rt = _.filter(skinPrickTests, {substance: rto});
      routineTests = routineTests.concat(rt);
      specificSkinPrickTests = _.reject(specificSkinPrickTests, {substance: rto});
    });


    routineTests = _.sortBy(routineTests, function(rt){
      return ROUTINE_TESTS.indexOf(rt);
    });

    specificSkinPrickTests = _.sortBy(specificSkinPrickTests, function(rt){
      return rt.substance;
    });
    return routineTests.concat(specificSkinPrickTests);
  }

  var isAtopic = function(skinPrickTests){
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

  return {
    sortTests: sortTests,
    ROUTINE_TESTS, ROUTINE_TESTS,
    CONTROL_TESTS: CONTROL_TESTS,
    STANDARD_TESTS: CONTROL_TESTS,
    isAtopic: isAtopic
  };
});
