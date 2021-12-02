angular.module('opal.controllers').controller('newRBHEpisode', function($modalInstance, FieldTranslator, $q, $scope, $http, episode, referencedata, refresh) {
	"use strict";

	$scope.episode = episode;
	$scope.editing = {}
	_.extend($scope, referencedata.toLookuplists());

	$scope.clean = function(){
		_.each(fields, function(field){
			if(field !== 'occld'){
				$scope.editing[field] = null;
			}
		});
	}

	$scope.close = function(){
		$modalInstance.close();
	}

	$scope.save = function(){
		var data = {
			referral: FieldTranslator.jsToSubrecord($scope.editing.referral, 'referral'),
			patient_id: $scope.episode.demographics[0].patient_id
		}
		$http.post('/indigo/v0.1/new_episode/', data).then(function(response){
			$q.when(refresh(response.data)).then(function(){
				$modalInstance.close();
			});
		});
	}
});
