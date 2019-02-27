describe('DemographicsSearch', function() {
    "use strict";
    var DemographicsSearch, $window, $httpBackend, ngProgressLite;
    var episode = {
      id: 10,
      demographics: [{
        patient_id: 12
      }]
    };

    var apiEndPoint, hn, callBacks;

    beforeEach(function(){
      module('opal.controllers');
      module('opal.services');
      inject(function($injector) {
        DemographicsSearch = $injector.get('DemographicsSearch');
        $window = $injector.get('$window');
        $httpBackend = $injector.get('$httpBackend');
        // ngProgressLite = $injector.get('ngProgressLite');
      });

      apiEndPoint = "/search/";
      hn = "111";
      callBacks = {
        patient_found_in_application: jasmine.createSpy(),
        patient_found_upstream: jasmine.createSpy(),
        patient_not_found: jasmine.createSpy()
      }
    });

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    it("should throw an error if there is an unexpected call back passed in", function(){
        callBacks["unexpected"] = "fail"
        expect(function(){ DemographicsSearch.find(apiEndPoint, hn, callBacks);}).toThrow();
    });

    it("should call patient found in application", function(){
        // $httpBackend.expectGET('/search/simple/?query=jane').respond(
        //     {object_list: [{categories: []}]}
        // )
    });

    it("should call patient found upstream", function(){

    });

    it("should call patient now found", function(){

    });

    it("should handle an unexpected response", function(){

    });

    it("should handle http error cases", function(){

    });
  });
