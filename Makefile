# Project makefile for a ska-tmc-low-integration project. You should normally only need to modify
# CAR_OCI_REGISTRY_USER and PROJECT below.
ALARM_HANDLER_FQDN= "alarm/handler/01"
CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-tmc-low-integration
TANGO_HOST ?= tango-databaseds:10000## TANGO_HOST connection to the Tango DS
TANGO_HOST_NAME ?= tango-databaseds
TELESCOPE ?= SKA-low
KUBE_NAMESPACE ?= ska-tmc-low-integration
KUBE_NAMESPACE_SDP ?= ska-tmc-integration-sdp
CSP_SIMULATION_ENABLED ?= true
SDP_SIMULATION_ENABLED ?= true
MCCS_SIMULATION_ENABLED ?= true
SDP_PROCCONTROL_REPLICAS ?= 1
K8S_TIMEOUT ?= 600s
PYTHON_LINT_TARGET ?= tests/
SN_COMMAND_TIMEOUT ?= 10


DEPLOYMENT_TYPE = $(shell echo $(TELESCOPE) | cut -d '-' -f2)
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g") ## What -m opt to pass to pytest

# run one test with FILE=acceptance/test_subarray_node.py::test_check_internal_model_according_to_the_tango_ecosystem_deployed
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
FILE_NAME?= alarm_rules.txt
EXIT_AT_FAIL = true ## Flag for determining exit at failure. Set 'true' to exit at first failure.
COUNT ?= 1

ifeq ($(EXIT_AT_FAIL),true)
ADD_ARGS += -x
endif

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
ifneq ($(CI_JOB_ID),)
KUBE_NAMESPACE ?= ci-$(CI_PROJECT_NAME)-$(CI_COMMIT_SHORT_SHA)
endif
# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=ska-tmc-testing-$(DEPLOYMENT_TYPE)
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
K8S_CHARTS ?= ska-tmc-$(DEPLOYMENT_TYPE) ska-tmc-testing-$(DEPLOYMENT_TYPE)## list of charts
K8S_CHART ?= $(HELM_CHART)

CLUSTER_DOMAIN ?= cluster.local
PORT ?= 10000
SUBARRAY_COUNT ?= 1
SDP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-sdp/control/0
SDP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-sdp/subarray
CSP_MASTER ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-csp/control/0
CSP_SUBARRAY_PREFIX ?= tango://$(TANGO_HOST_NAME).$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN):$(PORT)/low-csp/subarray
CI_REGISTRY ?= gitlab.com
K8S_TEST_IMAGE_TO_TEST ?=  harbor.skao.int/production/ska-tango-images-pytango-builder:9.4.2## docker image that will be run for testing purpose
TARANTA_ENABLED ?= false

CI_PROJECT_DIR ?= .
XRAY_TEST_RESULT_FILE = "build/cucumber.json"
XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0
JIVE ?= false# Enable jive
TARANTA ?= false
MINIKUBE ?= false ## Minikube or not
FAKE_DEVICES ?= false ## Install fake devices or not

ITANGO_DOCKER_IMAGE = $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-itango:9.3.10

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)

CI_PROJECT_PATH_SLUG ?= ska-tmc-low-integration
CI_ENVIRONMENT_SLUG ?= ska-tmc-low-integration


ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context -x
MARK ?= $(shell echo $(TELESCOPE) | sed "s/-/_/g")
endif

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE) --count=$(COUNT)

ifeq ($(CSP_SIMULATION_ENABLED),false)
CUSTOM_VALUES =	-f charts/ska-tmc-testing-low/tmc_csp_values.yaml
endif

ifeq ($(MCCS_SIMULATION_ENABLED),false)
CUSTOM_VALUES =	-f charts/ska-tmc-testing-low/tmc_mccs_values.yaml
endif

ifeq ($(SDP_SIMULATION_ENABLED),false)
CUSTOM_VALUES =	-f charts/ska-tmc-testing-low/tmc_sdp_values.yaml \
	--set global.sdp_master=$(SDP_MASTER)\
	--set global.sdp_subarray_prefix=$(SDP_SUBARRAY_PREFIX)\
	--set ska-sdp.proccontrol.replicas=$(SDP_PROCCONTROL_REPLICAS)\
	--set ska-sdp.helmdeploy.namespace=$(KUBE_NAMESPACE_SDP)
endif

K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set ska-tango-base.display=$(DISPLAY) \
	--set ska-tango-base.xauthority=$(XAUTHORITY) \
	--set ska-tango-base.jive.enabled=$(JIVE) \
	--set global.exposeAllDS=false \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.operator=true \
	--set ska-taranta.enabled=$(TARANTA_ENABLED)\
	--set tmc-low.subarray_count=$(SUBARRAY_COUNT)\
	--set tmc-low.deviceServers.subarraynode.CommandTimeOut=$(SN_COMMAND_TIMEOUT) \
	$(CUSTOM_VALUES)

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src \
							 TANGO_HOST=$(TANGO_HOST) \
							 TELESCOPE=$(TELESCOPE) \
							 KUBE_NAMESPACE=$(KUBE_NAMESPACE) \
							 KUBE_NAMESPACE_SDP=$(KUBE_NAMESPACE_SDP) \
							 CSP_SIMULATION_ENABLED=$(CSP_SIMULATION_ENABLED) \
							 SDP_SIMULATION_ENABLED=$(SDP_SIMULATION_ENABLED) \
							 MCCS_SIMULATION_ENABLED=$(MCCS_SIMULATION_ENABLED) \

K8S_TEST_TEST_COMMAND ?= $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
						pytest \
						$(PYTHON_VARS_AFTER_PYTEST) ./tests \
						| tee pytest.stdout # k8s-test test command to run in container

-include .make/k8s.mk
-include .make/helm.mk
-include .make/python.mk
-include .make/oci.mk
-include .make/xray.mk
-include .make/base.mk
-include PrivateRules.mak
-include resources/alarmhandler.mk

# to create SDP namespace
k8s-pre-install-chart:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif

# to create SDP namespace
k8s-pre-install-chart-car:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif
# to delete SDP namespace
k8s-post-uninstall-chart:
ifeq ($(SDP_SIMULATION_ENABLED),false)
	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
endif


taranta-link:
	@echo "#            https://k8s.stfc.skao.int/$(KUBE_NAMESPACE)/taranta/dashboard"

alarm-handler-configurator-link:
	@echo "#            https://k8s.stfc.skao.int/$(KUBE_NAMESPACE)/alarm-handler/"


cred:
	make k8s-namespace
	make k8s-namespace-credentials
test-requirements:
	@poetry export --without-hashes --with dev --format requirements.txt --output tests/requirements.txt
k8s-pre-test: test-requirements
