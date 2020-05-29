angular.module('opal.controllers').controller('InvestigationsCtrl', function($scope) {
  "use strict";

  var self = this;

  var ROUTINE_TEST_ORDER = [
    "Neg control",
    "Pos control",
    "Asp. fumigatus",
    "Grass pollen",
    "Cat",
    "House dust mite"
  ]


  var dateEquality = function(date1, date2){
    if(!date1 && !date2){
      return true;
    }
    if(date1 && !date2){
      return false;
    }
    if(!date1 && date2){
      return false
    }
    return date1.isSame(date2, "d")
  }

  this.filterByDate = function(someDate, skinPrickTests){
    return  _.filter(skinPrickTests, function(x){
      return dateEquality(x.date, someDate);
    });
  }

  this.skinPrickTestForDate = function(someDate, skinPrickTests){
    var forDate = self.filterByDate(someDate, skinPrickTests);

    var routineTests =[];

    _.each(ROUTINE_TEST_ORDER, function(rto){
      var rt = _.findWhere(forDate, {spt: rto});
      if(rt){
        routineTests.push(rt);
      }
      forDate = _.reject(forDate, {spt: rto})
    });

    routineTests = _.sortBy(routineTests, function(rt){
      return ROUTINE_TEST_ORDER.indexOf(rt);
    });

    forDate = _.sortBy(forDate, function(rt){
      return rt.spt;
    });
    var result = routineTests.concat(forDate);
    return routineTests.concat(forDate);
  };

  this.skinPrickTestDates = function(skinPrickTests){
    var result = [];

    _.each(skinPrickTests, function(skinPrickTest){
      if(!self.filterByDate(skinPrickTest.date, result).length){
        result.push(skinPrickTest)
      }
    });
    return _.pluck(result, "date");
  }
});