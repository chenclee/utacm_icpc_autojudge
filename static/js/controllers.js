var preContestControllers = angular.module('preContestControllers', []);

preContestControllers.controller('MainCtrl', ['$scope', '$http', '$timeout',
    function ($scope, $http, $timeout, $window) {
      function sync () {
        $http.get('api/v1/updates').success(function (data) {
          if ($scope.rawTime < parseInt(data['remaining_time'])) {
            $window.location.reload();
          }
          $scope.rawTime = data['remaining_time'];
          $scope.remainingTime = moment($scope.rawTime);
        });
        $timeout(sync, 5000);
        for (i = 1000; i <= 4000; i += 1000) {
          $timeout(tick, i);
        }
      }

      function tick () {
        $scope.rawTime -= 1;
        if ($scope.rawTime < 0) {
          $window.location.reload();
        } else {
          $scope.remainingTime = moment($scope.rawTime);
        }
      }

      sync();
    }]);

preContestControllers.controller('HomeCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);


var contestControllers = angular.module('contestControllers', []);
var probIds = [];

contestControllers.controller('MainCtrl', ['$scope', '$http', '$timeout', '$rootScope',
    function ($scope, $http, $timeout, $window) {
      $http.get('api/v1/metadata').success(function (data) {
        $scope.probIds = probIds = data['prob_ids'];
        $scope.probContents = data['prob_contents'];
      });

      function sync () {
        $http.get('api/v1/updates').success(function (data) {
          $scope.rawTime = data['remaining_time'];
          $scope.scoreboard = data['scoreboard'];
          $scope.clarifications = data['clarifications'];
          $scope.remainingTime = moment($scope.rawTime);
        });
        $timeout(sync, 5000);
        for (i = 1000; i <= 4000; i += 1000) {
          if ($scope.rawTime > 0) {
            $timeout(tick, i);
          }
        }
      }

      function tick () {
        $scope.rawTime -= 1;
        if ($scope.rawTime >= 0) {
          $scope.remainingTime = moment($scope.rawTime);
        }
      }

      sync();
    }]);

contestControllers.controller('HomeCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);

contestControllers.controller('AdminCtrl', ['$scope', '$http',
    function ($scope, $http) {
      $scope.processAddTimeInput = function(numMin) {
        submit_url = 'api/v1/admin/add_time/' + numMin;
        submit_data = { '_xsrf': $cookies._xsrf, 'content': numMin };
      }

      $scope.proccessClarifResponse = function(respNum, clarifNum) {
        submit_url = 'api/v1/admin/add_time/';
        submit_data = { '_xsrf': $cookies._xsrf, 'content': respNum };
      }
    }]);

contestControllers.controller('ProblemCtrl', ['$scope', '$http', '$rootScope', '$window', '$cookies',
    function ($scope, $http, $rootScope, $window, $cookies) {
      var tabClasses;
        
      function initTabs() {
        tabClasses = [];
        $scope.open = [];
        for (probId in probIds) {
          tabClasses.push("");
          $scope.open.push(false);
        }
      }
      
      $scope.getTabClass = function (tabNum) {
        return tabClasses[tabNum];
      };
      
      $scope.getTabPaneClass = function (tabNum) {
        return "tab-pane " + tabClasses[tabNum];
      }
      
      $scope.setActiveTab = function (tabNum) {
        initTabs();
        tabClasses[tabNum] = "active panel-primary";
        $rootScope.activeTab = tabNum;
        $scope.open[tabNum - 1] = true;
      };

      initTabs();
      if (typeof $rootScope.activeTab == 'undefined') {
        $scope.setActiveTab(1);
      } else {
        $scope.setActiveTab($rootScope.activeTab);
      }

      $scope.clarif = {}
      $scope.processClarifForm = function(probId) {
        submit_url = 'api/v1/submit/' + probIds[probId] + '/clarification';
        submit_data = { '_xsrf': $cookies._xsrf, 'content': $scope.clarif[probId] };
        $http({
          method  : 'POST',
          url     : submit_url,
          data    : $.param(submit_data),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function(data) {
          if (data) {
            $window.alert("clarif successfully submitted");
            $scope.clarif[probId] = "";
          }
        });
      }
    }]);

contestControllers.controller('ScoreboardCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);
