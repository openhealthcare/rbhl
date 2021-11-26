angular.module('opal.controllers').controller('MenuHelper', function($scope, $modal) {
	"use strict";
	var self = this;
	this.addEpisode = function(){
		$modal.open({
			controller: "ConfirmAddNewEpisode",
			templateUrl: 'templates/new_episode_confirmation.html',
			resolve: {
				refresh: function(){ return $scope.refresh; },
				patient: function(){ return $scope.patient; }
			}
		})
	}

	this.orderEpisodes = function(episodes){
		/*
		* Order episodes by -significant date.
		* For clinic episodes the significant date is the
		* clinic date, for blood episodes the significant date
		* is the blood date.
		* if there is no date, return the future
		*/
		var result = _.sortBy(episodes, function(episode){
			var sigDate = null;
			if(episode.referral[0].occld){
				sigDate = episode.clinic_log[0].clinic_date;
			}
			else{
				sigDate = self.findBloodDate(episode)
			}
			if(!sigDate){
				sigDate = moment(new Date(3000, 1, 1))
			}
			return sigDate;
		});
		return result.reverse();
	}


	this.findBloodDate = function(patient, episode){
		/*
		* Finds the earliest blood date for an episode
		* TLDR Make this work
		*/
		var result = _.find(patient.bloods, function(x){
			return x.blood_date;
		});
		if(result){
			return result.blood_date;
		}
	}
});
