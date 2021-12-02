angular.module('opal.controllers').controller('MenuHelper', function($scope, $modal) {
	"use strict";
	var self = this;
	this.addEpisode = function(episode){
		/*
		* Opens the add new episode modal. It takes
		* an episode because only an episode is
		* available when this is used in the
		* bloods pathway.
		*
		* We bind the refresh command to scope to
		* stop 'this' issues
		*/
		return $modal.open({
			controller: "newRBHEpisode",
			templateUrl: '/templates/new_episode.html',
			resolve: {
				refresh: function(){
					return function(responseData){ self.refreshEpisode(responseData.id) };
				},
				episode: function(){ return episode; },
				metadata: function(Metadata){ return Metadata.load(); },
				referencedata: function(Referencedata){ return Referencedata.load(); }
			}
		})
	}

	this.refreshEpisode = function(episodeId){
		$scope.refresh().then(function(){
			var idx = _.findIndex($scope.patient.episodes, {id: episodeId});
			$scope.switch_to_episode(idx);
		});
	}

	this.orderEpisodes = function(episodes){
		/*
		* Order episodes by -significant date.
		*/
		var result = _.sortBy(episodes, function(episode){
			var sigDate = episode.start
			if(sigDate){
				return sigDate
			}
			return moment(new Date(3000, 1, 1))
		});
		return result.reverse();
	}


	this.findBloodDate = function(episode){
		/*
		* Finds the earliest blood date for an episode.
		* because patient subrecords get copied onto the
		* episode, we look via the patient subrecord bloods
		* for subrecords with the episode id.
		*/
		var bloods = _.where(episode.bloods, {episode_id: episode.id});
		var bloodDates = _.map(bloods, function(blood){
			if(blood.blood_date){
				return blood.blood_date.toDate()
			}
		});
		// remove nulls
		bloodDates = _.compact(bloodDates)
		if(bloodDates.length){
			return _.min(bloodDates);
		}
	}
});
