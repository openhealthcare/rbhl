angular.module('opal.controllers').controller('DiagnosisDisplay', function($scope) {
  "use strict";

  this.open_modal = function(templateName){
    var toResolve =  {
      item: function() { return item; },
      profile: profile,
      episode: function() { return episode; },
      metadata: function(Metadata) { return Metadata.load(); },
      referencedata: function(Referencedata){ return Referencedata.load(); }
    }
    $scope.open_modal('EditItemCtrl', templateName, toResolve)
  }
});
