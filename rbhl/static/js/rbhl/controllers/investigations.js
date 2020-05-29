angular.module('opal.controllers').controller('InvestigationsCtrl', function($scope) {
  "use strict";

  var self = this;

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

  this.skinPrickTestForDate = function(someDate, skinPrickTests){
    var forDate = _.filter(skinPrickTests, function(x){
      return dateEquality(x.date, someDate);
    });

    var negControl = _.findWhere(forDate, {spt: "Neg control"});
    var posControl = _.findWhere(forDate, {spt: "Pos control"});
    var result = _.reject(forDate, function(spt){
      return spt === "Pos control" || spt === "Neg control"
    });

    if(negControl){
      result.unshift(negControl);
    }
    if(posControl){
      result.unshift(posControl);
    }
    return result;
  };

  this.skinPrickTestDates = function(skinPrickTests){
    var result = [];

    _.each(skinPrickTests, function(skinPrickTest){
      if(!self.skinPrickTestForDate(skinPrickTest.date, result).length){
        result.push(skinPrickTest)
      }
    });
    return _.pluck(result, "date");
  }
});