var preContestControllers = angular.module('preContestControllers', []);

preContestControllers.controller('MainCtrl', ['$scope', '$http', '$timeout', '$window',
    function ($scope, $http, $timeout, $window) {
      var first = true;
      function sync () {
        $http.get('api/v1/updates').success(function (data) {
          if (first || $scope.rawTime > data['remaining_time']) {
            $scope.rawTime = data['remaining_time'];
            first = false;
          }
          $scope.remainingTime = moment($scope.rawTime);
          $timeout(sync, 5000);
          for (i = 1000; i <= 4000; i += 1000) {
            $timeout(tick, i);
          }
        });
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

contestControllers.controller('MainCtrl', ['$scope', '$http', '$interval', '$rootScope',
    function ($scope, $http, $interval, $rootScope) {
      $http.get('api/v1/metadata').success(function (data) {
        $scope.probIds = probIds = data['prob_ids'];
        $scope.probContents = data['prob_contents'];
        $scope.langs = data['langs'];
        $scope.solved = data['solved'];
        $scope.verdicts = data['verdicts'];
      });

      $rootScope.syncUpdates = function () {
        $http.get('api/v1/updates').success(function (data) {
          if (typeof $rootScope.prevSync !== 'undefined')
            $interval.cancel($rootScope.prevSync);
          $rootScope.rawTime = data['remaining_time'];
          $scope.scoreboard = data['scoreboard'];
          $scope.solved = data['solved'];
          $scope.submissions = data['submissions'];
          $scope.clarifications = data['clarifications'];
          $rootScope.remainingTime = moment($rootScope.rawTime);
          $rootScope.prevSync = $interval($rootScope.clockTick, 1000, 4);
        });
      }

      $rootScope.clockTick = function () {
        $rootScope.rawTime -= 1;
        if ($rootScope.rawTime >= 0) {
          $rootScope.remainingTime = moment($rootScope.rawTime);
        }
      }

      $rootScope.syncUpdates();
      $interval($rootScope.syncUpdates, 5000);
    }]);

contestControllers.controller('HomeCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);

var whitelist = [];
var allClarifications = [];
var radioModel = 'Active';

contestControllers.controller('AdminCtrl', ['$scope', '$rootScope', '$http', '$cookies', '$window', '$modal', '$interval', '$window',
    function ($scope, $rootScope, $http, $cookies, $window, $modal, $interval) {
      function sync () {
        $http.get('api/v1/admin/updates').success(function (data) {
          $scope.whitelist = data.whitelist;
          $scope.allClarifications = data.clarifs;
          $scope.boardIsFrozen = data.frozen;
          $scope.radioModel = $scope.boardIsFrozen ? 'Frozen' : 'Active';
        });
      }
      sync();
      $interval(sync, 10000);

      $scope.rejudgeProblem = function(problemId) {
        submit_url = 'api/v1/admin/rejudge';
        submit_data = { '_xsrf': $cookies._xsrf, 'probId': problemId };
        $http({
          method  : 'POST',
          url     : submit_url,
          data    : $.param(submit_data),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function(data) {
          $window.alert("Rejudging problem " + problemId);
        });
      }

      $scope.processAddTimeInput = function(numMin) {
        submit_url = 'api/v1/admin/add_time';
        submit_data = { '_xsrf': $cookies._xsrf, 'numMin': numMin };
        $http({
          method  : 'POST',
          url     : submit_url,
          data    : $.param(submit_data),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function(data) {
          $scope.addTimeTextBox = null;
          $rootScope.syncUpdates();
        });
      }

      $scope.processClarifResponse = function(respNum, clarifNum) {
        submit_url = 'api/v1/admin/clarifications';
        var respString = '';
        if(respNum == 2) {
          $scope.clarifRespModalOpen(respNum, clarifNum)
        }
        else {
          submit_data = { '_xsrf': $cookies._xsrf, 'respNum': respNum, 'clarifNum': clarifNum, 'respString': '' };
          $http({
            method  : 'POST',
            url     : submit_url,
            data    : $.param(submit_data),
            headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
          }).success(function(data) {
            sync();
          });
        }
      }

      $scope.processAddAdminForm = function(newAdmin) {
        if (newAdmin == null)
          return;
        submit_url = 'api/v1/admin/whitelist';
        submit_data = { '_xsrf': $cookies._xsrf, 'newAdmin': newAdmin };
        $http({
          method  : 'POST',
          url     : submit_url,
          data    : $.param(submit_data),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function(data) {
          $scope.addAdminTextBox = null;
          sync();
        });

      }

      $scope.changeState = function(state) {
        submit_url = 'api/v1/admin/frozen';
        submit_data = { '_xsrf': $cookies._xsrf, 'state': state };
        $http({
          method  : 'POST',
          url     : submit_url,
          data    : $.param(submit_data),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function (data) {});
      }

      $scope.clarifRespModalOpen = function(respNum, clarifNum) {
        var modalInstance = $modal.open({
          templateUrl: 'clarifResponse.html',
          controller: 'ClarifRespModalCtrl',
          resolve: {
            respNum: function () {
              return respNum;
            },
            clarifNum: function() {
              return clarifNum;
            }
          }
        });

        modalInstance.result.then(function (response) {
          submit_url = 'api/v1/admin/clarifications'
          response['_xsrf'] = $cookies._xsrf;
              $http({
                method  : 'POST',
                url     : submit_url,
                data    : $.param(response),
                headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
              }).success(function(data) {
                sync();
              });
        }, function () {
        });
      };

      $scope.newClarification = function(index) {
        $scope.newClarifModalOpen($scope.probIds[index])
      }

      $scope.newClarifModalOpen = function(probId) {
        var modalInstance = $modal.open({
          templateUrl: 'newClarification.html',
          controller: 'NewClarifModalCtrl',
          resolve: {
            probId: function () {
              return probId;
            }
          }
        });

        modalInstance.result.then(function (response) {
          submit_url = 'api/v1/admin/clarification'
          response['_xsrf'] = $cookies._xsrf;
              $http({
                method  : 'POST',
                url     : submit_url,
                data    : $.param(response),
                headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
              }).success(function(data) {
                sync();
              });
        }, function () {
        });
      };

      var tabClasses;
  
      function initTabs() {
        tabClasses = ["","","",""];
      }
      
      $scope.getTabClass = function (tabNum) {
        return tabClasses[tabNum];
      };
      
      $scope.getTabPaneClass = function (tabNum) {
        return "tab-pane " + tabClasses[tabNum];
      }
      
      $scope.setActiveTab = function (tabNum) {
        initTabs();
        tabClasses[tabNum] = "active";
      };

      initTabs();
      $scope.setActiveTab(1);
    }]);

contestControllers.controller('ClarifRespModalCtrl', function ($scope, $modalInstance, respNum, clarifNum) {

  $scope.ok = function () {
    $modalInstance.close({
      'respNum': respNum,
      'clarifNum': clarifNum,
      'response': $scope.response,
    });
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
});

contestControllers.controller('NewClarifModalCtrl', function ($scope, $modalInstance, probId) {

  $scope.ok = function () {
    $modalInstance.close({
      'probId': probId,
      'response': $scope.newClarifResp,
    });
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
});

contestControllers.controller('ProblemCtrl', ['$scope', '$http', '$rootScope', '$window', '$cookies', '$interval', '$location',
    function ($scope, $http, $rootScope, $window, $cookies, $interval, $location) {
      var tabClasses;
        
      $scope.files = {};
      $scope.submLangs = [];
      $scope.files.source = [];
      i = 0;
      for (probId in probIds) {
        $scope.submLangs.push($scope.langs[0]);
        $scope.files.source.push(["", ""]);
      }

      function initTabs() {
        tabClasses = [];
        $scope.open = [];
        for (probId in probIds) {
          tabClasses.push("");
          $scope.open.push(false);
        }
      }
      
      $scope.getTabClass = function (tabNum) {
        if ($scope.solved[probIds[tabNum - 1]]) {
            return tabClasses[tabNum] + " panel-success";
        } else if ($rootScope.activeTab == tabNum) {
            return tabClasses[tabNum] + " panel-primary";
        }
      };
      
      $scope.getTabPaneClass = function (tabNum) {
        return "tab-pane " + tabClasses[tabNum];
      };
      
      $scope.setActiveTab = function (tabNum) {
        initTabs();
        tabClasses[tabNum] = "active";
        $rootScope.activeTab = tabNum;
        $scope.open[tabNum - 1] = true;
        $location.search('id=' + tabNum);
      };

      if (typeof $rootScope.activeTab == 'undefined') {
        if (!('id' in $location.search())) {
          $location.search('id=1');
        }
        $scope.setActiveTab(parseInt($location.search()['id']));
      } else {
        $scope.setActiveTab($rootScope.activeTab);
      }

      $scope.clarif = {}
      $scope.processClarifForm = function (index) {
        submitUrl = 'api/v1/submit/' + probIds[index] + '/clarification';
        submitData = { '_xsrf': $cookies._xsrf, 'content': $scope.clarif[index] };
        $http({
          method  : 'POST',
          url     : submitUrl,
          data    : $.param(submitData),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function (data) {
          if (data) {
            $window.alert("Clarification submitted successfully!");
            $scope.clarifications.push({
              'prob_id': probIds[index],
              'message': $scope.clarif[index],
            });
            $scope.clarif[index] = null;
          } else {
            $window.alert("Failed to submit. Try again!");
          }
        });
      };

      $scope.processSubmitForm = function (index) {
        submitUrl = 'api/v1/submit/' + probIds[index] + '/solution';
        submitData = { '_xsrf': $cookies._xsrf,
                       'lang': $scope.submLangs[index],
                       'filename': $scope.files.source[index][0],
                       'sourceFile': $scope.files.source[index][1], };
        $http({
          method  : 'POST',
          url     : submitUrl,
          data    : $.param(submitData),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function (data) {
          if (data) {
            $window.alert("Submitted successfully!");
          } else {
            $window.alert("Failed to submit. Try again!");
          }
        });
      };
    }]);

contestControllers.controller('ScoreboardCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);

contestControllers.controller('SubmissionsCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);
