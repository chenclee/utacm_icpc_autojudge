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
    function ($scope, $http, $interval, $rootScope, $window) {
      $http.get('api/v1/metadata').success(function (data) {
        $scope.probIds = probIds = data['prob_ids'];
        $scope.probContents = data['prob_contents'];
        $scope.remainingPermits = data['remaining_permit_counts'];
        $scope.solved = data['solved'];
        $scope.problemsTimeToSolve = data['problems_time_to_solve'];

        for (var i = 0; i < probIds.length; i++) {
          $scope.problemsTimeToSolve[probIds[i]] = momentMinutes($scope.problemsTimeToSolve[probIds[i]]);
        }
      });

      $rootScope.syncUpdates = function () {
        $http.get('api/v1/updates').success(function (data) {
          if (typeof $rootScope.prevSync !== 'undefined')
            $interval.cancel($rootScope.prevSync);
          $rootScope.rawTime = data['remaining_time'];
          $scope.scoreboard = data['scoreboard'];
          $scope.clarifications = data['clarifications'];
          $rootScope.remainingTime = moment($rootScope.rawTime);
          $rootScope.prevSync = $interval($rootScope.clockTick, 1000, 29);
        });
      }

      $rootScope.clockTick = function () {
        $rootScope.rawTime -= 1;
        if ($rootScope.rawTime >= 0) {
          $rootScope.remainingTime = moment($rootScope.rawTime);
        }
      }

      $rootScope.syncUpdates();
      $interval($rootScope.syncUpdates, 30000);
    }]);

contestControllers.controller('HomeCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);

var whitelist = [];
var allClarifications = [];
var radioModel = 'Active';

contestControllers.controller('AdminCtrl', ['$scope', '$rootScope', '$http', '$cookies', '$window', '$modal', '$interval',
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

contestControllers.controller('ProblemCtrl', ['$scope', '$http', '$rootScope', '$window', '$cookies', '$interval',
    function ($scope, $http, $rootScope, $window, $cookies, $interval) {
      var tabClasses;
        
      $scope.files = {};
      $scope.files.output = [];
      $scope.files.source = [];
      i = 0;
      for (probId in probIds) {
        $scope.files.output.push("");
        $scope.files.source.push("");
      }
      if (typeof $rootScope.showSubmit == 'undefined') {
        $rootScope.showSubmit = [];
        $rootScope.ttl = [];
        $rootScope.ttlText = [];
        $rootScope.tick = [];
        for (probId in probIds) {
          $rootScope.showSubmit.push(false);
          $rootScope.ttl.push(-1);
          $rootScope.ttlText.push("");
          $rootScope.tick.push(null);
        }
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
        } else if ($scope.remainingPermits[probIds[tabNum - 1]] == 0) {
            return tabClasses[tabNum] + " panel-danger";
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
      };

      if (typeof $rootScope.activeTab == 'undefined') {
        $scope.setActiveTab(1);
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
          }
        });
      };

      function tick (index) {
        $rootScope.ttl[index] -= 1;
        $rootScope.ttlText[index] = momentMinutes($rootScope.ttl[index]);
        if ($rootScope.ttl[index] <= 0) {
          $rootScope.showSubmit[index] = false;
          if ($rootScope.tick[index] != null) {
            $interval.cancel($rootScope.tick[index]);
            $rootScope.tick[index] = null;
          }
        }
      }

      $scope.getPermit = function (index, create) {
        permitUrl = 'api/v1/permits';
        permitData = { '_xsrf': $cookies._xsrf, 'content': probIds[index], 'create': create };
        $http({
          method  : 'POST',
          url     : permitUrl,
          data    : $.param(permitData),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function (data) {
          if (data == null && !create)
            return;
          if ($rootScope.tick[index] != null) {
            $interval.cancel($rootScope.tick[index]);
            $rootScope.tick[index] = null;
          }
          if (data === 'solved') {
            $scope.solved[probIds[index]] = true;
            return;
          }
          if (data.is_new)
            $scope.remainingPermits[probIds[index]]--;
          $rootScope.showSubmit[index] = true;
          $rootScope.ttl[index] = data.ttl;
          $rootScope.ttlText[index] = momentMinutes($rootScope.ttl[index]);
          $rootScope.tick[index] = $interval(function () {
            tick(index);
          }, 1000, data.ttl);
        }).error(function (data, status, headers, config) {
          if (create && status == 403) {
            $window.alert("You are out of permits!");
          }
        });
      };

      var i = 0;
      for (probId in probIds) {
        $scope.getPermit(i, false);
        i++;
      }

      $scope.processSubmitForm = function (index) {
        submitUrl = 'api/v1/submit/' + probIds[index] + '/solution';
        submitData = { '_xsrf': $cookies._xsrf,
                       'outputFile': $scope.files.output[index],
                       'sourceFile': $scope.files.source[index], };
        $rootScope.showSubmit[index] = false;
        $rootScope.ttl[index] = 0;
        if ($rootScope.tick[index] != null) {
          $interval.cancel($rootScope.tick[index]);
          $rootScope.tick[index] = null;
        }
        $http({
          method  : 'POST',
          url     : submitUrl,
          data    : $.param(submitData),
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' },
        }).success(function (data) {
          if (data) {
            $scope.solved[probIds[index]] = true;
            $window.alert("Solution accepted!");
          } else {
            $window.alert("Solution incorrect!");
          }
        });
      };
    }]);

contestControllers.controller('ScoreboardCtrl', ['$scope', '$http',
    function ($scope, $http) {
    }]);
