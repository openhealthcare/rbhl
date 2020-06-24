angular.module('opal.controllers').controller(
  'SkinPrickTestController', function(scope, step, episode, displayDateFilter, $location, SkinPrickTestHelper) {
    /*
    * A patient comes in and undergoes a set of skin prick tests.
    * date is the date they have the tests, antihistamines is if the
    * patient is on antihistamines at the time of the test.
    *
    * The pathway therefore looks at one date.
    *
    * The controller for adding skin prick tests.
    * We expect a GET parameter of 'date'
    *
    * If they don't have skin prick test for that date create a set
    * of the common skin prick tests for that date with the
    * antihistamines set the value of the get parameter
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
      * {skin_prick_test: {substance: 'rats}},
      * {skin_prick_test: {substance: 'grain'}},
      * ]
      *
      * scope.add accepts an object of e.g. {substance: 'mice'}
      * and adds it to the array of skin prick tests ie
      * scope.skin_prick_tests now equals
      *
      * [
      * {skin_prick_test: {substance: 'rats}},
      * {skin_prick_test: {substance: 'grain'}},
      * {skin_prick_test: {substance: 'mice'}},
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
        antihistamines: scope.antihistamines,
        wheal: 0,
        _client: {
          id: _.uniqueId("testRow"),
          error: ""
        }
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
        spt.skin_prick_test.antihistamines = scope.antihistamines;
      });
      scope.validate();
    }

    scope.updateDates = function(){
      /*
      * Changing the date field at the top of the page changes
      * the date for all tests
      */
      _.each(scope.skin_prick_tests, function(spt){
        spt.skin_prick_test.date = scope.testingDate;
      });
      scope.validate();
    }

    scope.toSaveSet = function(){
      /*
      * Combine all the skin prick tests for this patient.
      *
      * Remove the ones that have been deleted in this form.
      * Update the ones that have been changed.
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

     var result = otherDates.concat(newOrEditedSpts);
     return result;
    }

    scope.preSave = function(editing){
      editing.skin_prick_test = scope.toSaveSet()
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
      return moment(date1).isSame(moment(date2), "d")
    }

    scope.testsForDate = function(){
      scope.skin_prick_tests = [];
      if($location.search().new){
        _.each(SkinPrickTestHelper.ROUTINE_TESTS, function(routine_spt){
          var args = scope.getDefaultArgs();
          args.substance = routine_spt;
          scope.add(args);
        });
      }
      else{
        var date = scope.getDateFromGetParams();
        if(scope.editing.skin_prick_test && scope.editing.skin_prick_test.length){
          if(_.isArray(scope.editing.skin_prick_test)){
            var skinPrickTests = _.filter(scope.editing.skin_prick_test, function(spt){
              return scope.dateEquality(spt.date, date)
            })
            if(skinPrickTests.length){
              skinPrickTests = SkinPrickTestHelper.sortTests(skinPrickTests);
              _.each(skinPrickTests, function(spt){scope.add(spt)});
            }
          }
          else if(scope.dateEquality(scope.editing.skin_prick_test.date, date)){
            scope.add(scope.editing.skin_prick_test)
          }
        }
      }
    }

    scope.dateError = function(spt){
      var dtString = displayDateFilter(spt.date);
      return "For the date " + dtString + " it is unclear if the patient was on antihistamines or not.";
    }

    scope.isSkinPrickTestValid = function(spt){
      /*
      * spt.antihistamines actually means on this day the patient was on anthistimines
      * therefore an spt is invalid if for a day a patient is both recorded as being
      * on and not on antihistamines
      */
      spt._client.error = ""

      if(!spt.substance || !spt.substance.length){
        spt._client.error = "A substance is required"
        return
      }
      else if(spt.wheal === null || spt.wheal === undefined){
        spt._client.error = "A wheal is required"
        return
      }

      scope.allSpts = scope.toSaveSet();
      var different = _.find(scope.allSpts, function(otherSpt){
        var otherAntihistimines = !!otherSpt.antihistamines;
        var onAntihistimines = !!spt.antihistamines;
        return scope.dateEquality(otherSpt.date, spt.date) && (otherAntihistimines !== onAntihistimines);
      });

      if(different){
        spt._client.error = scope.dateError(spt);
      }
    }

    scope.validate = function(){
      _.each(scope.skin_prick_tests, function(sptRow){
        scope.isSkinPrickTestValid(sptRow.skin_prick_test);
      });
      return scope.isValid();
    }


    scope.getFlawedRow = function(){
      return _.find(scope.skin_prick_tests, function(sptRow){
        return sptRow.skin_prick_test._client.error.length;
      });
    }

    scope.isValid = function(){
      var row = scope.getFlawedRow();
      if(row){
        return false;
      }
      return true;
    }

    var init = function(){
      /*
      * If the patient already has tests for GET.date
      * display the skin prick tests.
      *
      * Otherwise create a list of the common skin prick
      * tests setting GET.date and GET.antihistamines for
      * each.
      */
      scope.testingDate = scope.getDateFromGetParams();
      scope.testsForDate();
      scope.antihistamines = _.every(scope.skin_prick_tests, function(spt){
        return spt.skin_prick_test.antihistamines;
      });
      scope.initialTests = _.clone(scope.skin_prick_tests);
      scope.validate();
    }

    init();
  });