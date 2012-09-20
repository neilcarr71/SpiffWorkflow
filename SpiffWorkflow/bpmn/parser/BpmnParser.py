import glob
import os
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn.specs.BoundaryEvent import BoundaryEvent
from SpiffWorkflow.bpmn.specs.CallActivity import CallActivity
from SpiffWorkflow.bpmn.specs.ExclusiveGateway import ExclusiveGateway
from SpiffWorkflow.bpmn.specs.IntermediateCatchEvent import IntermediateCatchEvent
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.specs.StartEvent import StartEvent
from SpiffWorkflow.bpmn.specs.UserTask import UserTask
from SpiffWorkflow.bpmn.specs.EndEvent import EndEvent
from SpiffWorkflow.bpmn.parser.ProcessParser import ProcessParser
from SpiffWorkflow.bpmn.parser.util import *
from SpiffWorkflow.bpmn.parser.task_parsers import *
from lxml import etree

__author__ = 'matth'

class BpmnParser(object):

    PARSER_CLASSES = {
        full_tag('startEvent')          : (StartEventParser, StartEvent),
        full_tag('endEvent')            : (EndEventParser, EndEvent),
        full_tag('userTask')            : (UserTaskParser, UserTask),
        full_tag('manualTask')          : (ManualTaskParser, ManualTask),
        full_tag('exclusiveGateway')    : (ExclusiveGatewayParser, ExclusiveGateway),
        full_tag('parallelGateway')     : (ParallelGatewayParser, ParallelGateway),
        full_tag('callActivity')        : (CallActivityParser, CallActivity),
        full_tag('scriptTask')                  : (ScriptTaskParser, ScriptTask),
        full_tag('intermediateCatchEvent')      : (IntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('boundaryEvent')               : (BoundaryEventParser, BoundaryEvent),
        }

    OVERRIDE_PARSER_CLASSES = {}

    PROCESS_PARSER_CLASS = ProcessParser
    WORKFLOW_CLASS = BpmnWorkflow

    def __init__(self):
        self.process_parsers = {}
        self.process_parsers_by_name = {}

    def get_parser_class(self, tag):
        if tag in self.OVERRIDE_PARSER_CLASSES:
            return self.OVERRIDE_PARSER_CLASSES[tag]
        else:
            return self.PARSER_CLASSES[tag]

    def get_process_parser(self, process_id_or_name):
        if process_id_or_name in self.process_parsers_by_name:
            return self.process_parsers_by_name[process_id_or_name]
        else:
            return self.process_parsers[process_id_or_name]

    def add_bpmn_file(self, filename):
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        for filename in filenames:
            f = open(filename, 'r')
            try:
                self.add_bpmn_fp(f, None, filename)
            finally:
                f.close()

    def add_bpmn_fp(self, fp, svg_fp=None, filename=None):
        xpath = xpath_eval(etree.parse(fp))
        svg = etree.parse(svg_fp) if svg_fp is not None else None

        processes = xpath('//bpmn:process')
        for process in processes:
            process_parser = self.PROCESS_PARSER_CLASS(self, process, svg, filename=filename)
            if process_parser.get_id() in self.process_parsers:
                raise ValueError('Duplicate processes with ID "%s"', process_parser.get_id())
            if process_parser.get_name() in self.process_parsers_by_name:
                raise ValueError('Duplicate processes with name "%s"', process_parser.get_name())
            self.process_parsers[process_parser.get_id()] = process_parser
            self.process_parsers_by_name[process_parser.get_name()] = process_parser

    def _parse_condition(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        xpath = xpath_eval(sequence_flow_node)
        condition_expression_node = conditionExpression = first(xpath('.//bpmn:conditionExpression'))
        if conditionExpression is not None:
            conditionExpression = conditionExpression.text
        return self.parse_condition(conditionExpression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node)

    def parse_condition(self, condition_expression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node):
        return condition_expression

    def get_spec(self, process_id_or_name):
        return self.get_process_parser(process_id_or_name).get_spec()



