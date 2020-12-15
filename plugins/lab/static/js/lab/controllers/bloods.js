angular.module('opal.controllers').controller(
  'BloodsStep', function(scope, step, episode, $window, $location, $modal) {
  "use strict"
  /*
  * The bloods step works on a single bloods instance.
  * if there is an id as a GET param in the url, then it is that instance
  * otherwise we create a new one.
  */
  var init = function(){
    var bloodTest;
    scope.bloodTest = null;
    var id = $location.search().id;
    if(!id){
      bloodTest = {};
    }
    else{
      bloodTest = _.findWhere(scope.editing.bloods, {id: parseInt(id)});
      if(!bloodTest){
        alert('Unable to find bloods');
      }
    }
    scope.bloodTest = {bloods: bloodTest};
  }

  scope.addResult = function(){
    if(!scope.bloodTest.bloods.bloodresult){
      scope.bloodTest.bloods.bloodresult = [];
    }
    scope.bloodTest.bloods.bloodresult.push({});
  }

  scope.removeResult = function(idx){
    scope.bloodTest.bloods.bloodresult.splice(idx, 1);
  }

  scope.selectAllergen = function($item, result){
    if($item){
      result.antigenno = $item.code
    }
  }


  scope.delete = function(){
    var item = _.findWhere(episode.bloods, {id: scope.bloodTest.bloods.id})
    var deleteModal =  $modal.open({
      templateUrl: '/templates/pathway/delete_bloods_modal.html',
      controller: 'DeleteItemConfirmationCtrl',
      resolve: {
        item: item
      }
    });
    deleteModal.result.then(function(result){
      if(result === 'deleted'){
        $window.location.href = "/#/patient/" + item.patient_id + "/investigations";
      }
    });
  }

  scope.preSave = function(editing){
    var urlId = $location.search().id;
    urlId = parseInt(urlId);

    // there should always be a bloodTest but potentially
    // if it was unable to find the bloods then this
    // would not be the case.
    if(scope.bloodTest){
      if(urlId){
        var idx = _.findIndex(editing.bloods, function(bb){
          return bb.id === urlId;
        });
        editing.bloods[idx] = scope.bloodTest.bloods;
      }
      else{
        editing.bloods.push(scope.bloodTest.bloods);
      }
    }
  }

  init();
});