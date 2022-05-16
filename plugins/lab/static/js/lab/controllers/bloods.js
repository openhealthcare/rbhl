angular.module('opal.controllers').controller(
  'BloodsStep', function(scope, step, episode, $window, $location, $modal, displayDateFilter) {
  "use strict"
  /*
  * The bloods step works on a single bloods instance.
  * if there is an id as a GET param in the url, then it is that instance
  * otherwise we create a new one.
  */
  var init = function(){
    var bloodTest;
    scope.bloodTest = null;
		scope.patient_id = scope.episode.demographics[0].patient_id;
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

  scope.referral_display = function(referral){
    /*
    * Options do not allow if statements so we format the display
    * name of the employment in here.
    */
    var result = displayDateFilter(referral.date_of_referral) || "";
    result = result + " " + referral.referrer_name;
    if(result && referral.reference_number){
      result += " (" + referral.reference_number + ")";
    }
    return result;
  }

  scope.addSubrecord = function(subrecordName){
    /*
    * The form has a select box to choose existing employent/referral subrecords.
    * If a subrecord does not exist, this allows them to create one.
    *
    *
    * Employer used to be a singleton
    * if there is a model with no creted timestamp
    * use that rather than creating a new employment model
    */
    var subrecordSet = episode[subrecordName];
    var subrecord = _.find(subrecordSet, function(subrecord){
      return !subrecord.created && !subrecord.updated;
    });
    if(subrecord){
      episode.recordEditor.editItem(subrecordName, subrecord).then(function(result){
        if(result == 'deleted' || result == 'cancel'){
          return;
        }
        var field = subrecordName + "_id";
        scope.bloodTest.bloods[field] = subrecord.id;
      });
    }
    else{
      var idsBefore = _.pluck(subrecordSet, "id");
      episode.recordEditor.newItem(subrecordName).then(function(result){
        if(result == 'deleted' || result == 'cancel'){
          return;
        }
        // find the new id that's been added
        var idsAfter = _.pluck(episode[subrecordName], "id");
        var newIds = _.difference(idsAfter, idsBefore);
        if(newIds.length){
          var field = subrecordName + "_id";
          scope.bloodTest.bloods[field] = newIds[0];
        }
      });
    }
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
		/*
		* Update the phadia test code for the allergen if a test code exists
		* this is called from typeahead
		*/
    if($item && $item.code){
      result.phadia_test_code = $item.code;
    }
		else{
			result.phadia_test_code = null;
		}
  }

	scope.typedAllergen = function(result){
		/*
		* Update the phadia test code for the allergen if a test code exists
		* this is called if the user types in the allergen box
		*/
		if(!result.allergen || !!result.allergen.length){
			result.phadia_test_code = null;
		}
		var phadiaCode = _.findWhere(scope.metadata.phadia_test_code, {name: result.allergen});
		if(phadiaCode){
			result.phadia_test_code = phadiaCode.code;
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
