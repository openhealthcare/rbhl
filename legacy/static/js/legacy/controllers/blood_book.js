angular.module('opal.controllers').controller(
  'BloodBookStep', function(scope, step, episode, $window, $location, $modal) {
  "use strict"
  /*
  * The blood book step works on a single blood book instance.
  * if there is an id as a GET param in the url, then it is that instance
  * otherwise we create a new one.
  */
  var init = function(){
    var bloodBookTest;
    scope.bloodBookTest = null;
    var id = $location.search().id;
    if(!id){
      bloodBookTest = {};
    }
    else{
      bloodBookTest = _.findWhere(scope.editing.blood_book, {id: parseInt(id)});
      if(!bloodBookTest){
        alert('Unable to find blood book');
      }
    }
    scope.bloodBookTest = {blood_book: bloodBookTest};
  }

  scope.addResult = function(){
    if(!scope.bloodBookTest.blood_book.bloodbookresult){
      scope.bloodBookTest.blood_book.bloodbookresult = [];
    }
    scope.bloodBookTest.blood_book.bloodbookresult.push({});
  }

  scope.removeResult = function(idx){
    scope.bloodBookTest.blood_book.bloodbookresult.splice(idx, 1);
  }

  scope.delete = function(){
    var item = _.findWhere(episode.blood_book, {id: scope.bloodBookTest.blood_book.id})
    var deleteModal =  $modal.open({
      templateUrl: '/templates/pathway/delete_blood_book_modal.html',
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

    // there should always be a bloodBookTest but potentially
    // if it was unable to find the blood book then this
    // would not be the case.
    if(scope.bloodBookTest){
      if(urlId){
        var idx = _.findIndex(editing.blood_book, function(bb){
          return bb.id === urlId;
        });
        editing.blood_book[idx] = scope.bloodBookTest.blood_book;
      }
      else{
        editing.blood_book.push(scope.bloodBookTest.blood_book);
      }
    }
  }

  init();
});