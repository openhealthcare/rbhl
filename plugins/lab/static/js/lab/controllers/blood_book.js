angular.module('opal.controllers').controller(
  'BloodBookStep', function(scope, step, episode, $location) {
  /*
  * The blood book step works on a single blood book instance.
  * if there is an id as a GET param in the url, then it is that instance
  * otherwise we create a new one.
  */
  var init = function(){
    scope.bloodBookTest = null;
    var id = $location.search().id;
    if(!id){
      scope.bloodBookTest = {};
    }
    else{
      scope.bloodBookTest = _.findWhere(scope.editing.blood_book, {id: id});
      if(!scope.bloodBookTest){
        alert('Unable to find blood book');
      }
    }
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
        editing.blood_book[idx] = scope.bloodBookTest;
      }
      else{
        editing.blood_book.push(scope.bloodBookTest);
      }
    }
  }
});