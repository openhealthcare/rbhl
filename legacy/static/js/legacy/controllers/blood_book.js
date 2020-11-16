angular.module('opal.controllers').controller(
  'BloodBookStep', function(scope, step, episode, $location) {
  /*
  * The blood book step works on a single blood book instance.
  * if there is an id as a GET param in the url, then it is that instance
  * otherwise we create a new one.
  */
  var init = function(){
    var bloodBookTest;
    scope.bloodBookTest = null;
    var id = $location.search().id;
    // foreign keys aren't copy over so we have to manually copy them
    // over to post back.
    // we don't need serialization because there are no date fields
    _.each(episode.blood_book, function(bb){
      var editingBB = _.findWhere(scope.editing.blood_book, {id: bb.id});
      editingBB.bloodbookresult_set = bb.bloodbookresult_set;
    });

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
    if(!scope.bloodBookTest.blood_book.bloodbookresult_set){
      scope.bloodBookTest.blood_book.bloodbookresult_set = [];
    }
    scope.bloodBookTest.blood_book.bloodbookresult_set.push({});
  }

  scope.removeResult = function(idx){
    scope.bloodBookTest.blood_book.bloodbookresult_set.splice(idx, 1);
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