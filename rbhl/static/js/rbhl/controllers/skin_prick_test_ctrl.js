angular.module('opal.controllers').controller(
  'SkinPrickTestController', function(scope, step, episode, $location) {
    /*
    * A patient comes in and undergoes a set of skin prick tests.
    * date is the date they have the tests, antihistimines is if the
    * patient is on antihistimines at the time of the test.
    *
    * The pathway therefore looks at one date.
    *
    * The controller for adding skin prick tests.
    * We expect a GET parameter of 'date' and one of 'antihistmimines'
    *
    * If the patient already has skin prick tests for that date show
    * all the skin prick tests.
    *
    * If they don't have skin prick test for that date create a set
    * of the common skin prick tests for that date with the
    * antihistimines set t the value of the get parameter
    */

    "use strict";

    scope.remove = function(idx){
      scope.skin_prick_tests.splice(idx, 1);
    }

    scope.add = function(args){
      /*
      * The pathway expects an array on scope.skin_prick_tests
      * of a format like
      * [
      * {skin_prick_test: {spt: 'rats}},
      * {skin_prick_test: {spt: 'grain'}},
      * ]
      *
      * scope.add accepts an object of e.g. {spt: 'mice'}
      * and adds it to the array of skin prick tests ie
      * scope.skin_prick_tests now equals
      *
      * [
      * {skin_prick_test: {spt: 'rats}},
      * {skin_prick_test: {spt: 'grain'}},
      * {skin_prick_test: {spt: 'mice'}},
      * ]
      */
      var editing = {skin_prick_test: args}
      scope.skin_prick_tests.push(editing)
    }

    scope.getDateFromGetParams = function(){
      /*
      * Get's the date from the GET params and formats it to a date.
      * if the data param is empty, by default that will give you
      * an empty string, this function will return null instead.
      */
      var date = $location.search().date;
      if(date){
        date = new Date(date)
      }
      else{
        date = null;
      }

      return date;
    }

    scope.getDefaultArgs = function(){
      return {
        date: scope.testingDate,
        antihistimines: scope.antihistimines
      }
    }

    scope.addAnother = function(){
      scope.add(scope.getDefaultArgs());
    }

    scope.updateAntihistimines = function(){
      /*
      * Changing the antihistmine field at the top of the page changes
      * the antihistmine for all tests.
      */
      _.each(scope.skin_prick_tests, function(spt){
        spt.skin_prick_test.antihistimines = scope.antihistimines;
      });
    }

    scope.updateDates = function(){
      /*
      * Changing the date field at the top of the page changes
      * the date for all tests
      */
      _.each(scope.skin_prick_tests, function(spt){
        spt.skin_prick_test.date = scope.testingDate;
      });
    }

    scope.preSave = function(editing){
      /*
      * Look at the tests initially loaded from the get parameter.
      * Remove any of the for the date.
      * These will either have been deleted or editted.
      * Add in everything from scope.skin_prick_tests.
      */
      var existingIds = _.map(scope.initialTests, function(spt){
       return spt.skin_prick_test.id;
      });
      var existingIds = _.compact(existingIds);

      var otherDates = _.reject(scope.editing.skin_prick_test, function(spt){
        return _.contains(existingIds, spt.id);
      })
      var newOrEditedSpts = _.map(scope.skin_prick_tests, function(x){
        return x.skin_prick_test;
      })
      editing.skin_prick_test = otherDates.concat(newOrEditedSpts);
    };

    scope.dateEquality = function(date1, date2){
      if(!date1 && !date2){
        return true;
      }
      if(date1 && !date2){
        return false;
      }
      if(!date1 && date2){
        return false
      }
      return date1.getTime() === date2.getTime()
    }

    scope.testsForDate = function(){
      scope.skin_prick_tests = [];
      var date = scope.getDateFromGetParams();
      if(scope.editing.skin_prick_test && scope.editing.skin_prick_test.length){
        if(_.isArray(scope.editing.skin_prick_test)){
          var skinPrickTests = _.filter(scope.editing.skin_prick_test, function(spt){
            return scope.dateEquality(spt.date, date)
          })
          if(skinPrickTests.length){
            _.each(skinPrickTests, function(spt){scope.add(spt)});
          }
        }
        else if(scope.dateEquality(scope.editing.skin_prick_test.date, date)){
          scope.add(scope.editing.skin_prick_test)
        }
      }

      if(!scope.skin_prick_tests.length){
        var routine_spts = [
          "Neg control",
          "Pos control",
          "Asp. fumigatus",
          "Grass pollen",
          "Cat",
          "House dust mites"
        ]
        _.each(routine_spts, function(routine_spt){
          var args = scope.getDefaultArgs();
          args.spt = routine_spt;
          scope.add(args);
        });
      }
    }

    var init = function(){
      /*
      * If the patient already has tests for GET.date
      * display the skin prick tests.
      *
      * Otherwise create a list of the common skin prick
      * tests setting GET.date and GET.antihistimines for
      * each.
      */
      scope.testingDate = scope.getDateFromGetParams();
      scope.testsForDate();
      scope.initialTests = _.clone(scope.skin_prick_tests);
    }

    init();
  });