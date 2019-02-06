import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

    def kb_explain(self, fact_or_rule):
        """
        Explain where the fact or rule comes from

        Args:
            fact_or_rule (Fact or Rule) - Fact or rule to be explained

        Returns:
            string explaining hierarchical support from other Facts and rules
        """
        ####################################################
        # Student code goes here
        # created a variable to keep track of the level of indentation
        indent = 0
        if isinstance(fact_or_rule, Fact):
            # if fact_or_Rule is in fact a Fact,
            # get the pointer to the actual fact in the KB
            fact_or_rule = self._get_fact(fact_or_rule)
            # check if this fact is in fact in the KB
            if fact_or_rule in self.facts:
                # for fact, we simply need to access the statement field and convert to string
                fact_string = "fact: " + str(fact_or_rule.statement)
                # then we check whether or not we need to add an ASSERTED tag
                if fact_or_rule.asserted:
                    fact_string += " ASSERTED"
                # finally change lines
                fact_string += "\n"
                # now we check whether the fact has any fact-rule pairs in its supported by list
                if len(fact_or_rule.supported_by) > 0:
                    # for each fact-rule support, i will append the result of my helper function
                    # to the ongoing string
                    # i also pass the indent value to keep track
                    for support in fact_or_rule.supported_by:
                        fact_string += self.add_support(support, indent)
                # print(fact_string)
                # finally, return resulting string
                return fact_string
            else:
                # if fact is not in the KB
                e_string = "Fact is not in the KB"
                return e_string
        elif isinstance(fact_or_rule, Rule):
            # if fact_or_rule is in fact a Rule,
            # get the pointer to the actual rule in the KB
            fact_or_rule = self._get_rule(fact_or_rule)
            # check if this rule is in fact in the KB
            if fact_or_rule in self.rules:
                # for rule, it is slightly more complicated
                # first we add first element of the lhs of the rule
                rule_string = "rule: ("
                rule_string += fact_or_rule.lhs[0]
                # then for each subsequent item in the list of lhs items,
                # we add a comma followed by the lhs element
                for left in fact_or_rule.lhs[1:]:
                    rule_string += ", " + str(left)
                # finally, we add an arrow showing that it implies the rhs of the rule
                rule_string += ") -> " + str(fact_or_rule.rhs)
                # now we check whether or not we need to add the ASSERTED flag
                if fact_or_rule.asserted:
                    rule_string += " ASSERTED"
                rule_string += "\n"
                # create new line
                if len(fact_or_rule.supported_by) > 0:
                    # for each fact-rule support, i will append the result of my helper function
                    # to the ongoing string
                    # i also pass the indent value to keep track
                    for support in fact_or_rule.supported_by:
                        rule_string += self.add_support(support, indent)
                # print(rule_string)
                # finally return the resulting string
                return rule_string
            else:
                # if rule is not in the KB
                e_string = "Rule is not in the KB"
                return e_string

    def add_support(self, pair, ind):
        # helper function to print the entire SUPPORTED BY area of the result string
        # helper function will be passed a fact-rule pair and an indentation level
        # helper function will be recursively called for all supports of supports to fact_or_rule
        indent = ind + 1
        # add a level of indentation each time recursively called
        s_string = ""
        for i in range(indent):
            s_string += "  "
        # add the number of indentations so far
        s_string += "SUPPORTED BY" + "\n"
        s_fact = pair[0]
        # extract the fact from the fact-rule pair
        s_rule = pair[1]
        # extract the rule from the fact-rule pair
        for i in range(indent):
            s_string += "  "
        # again, add the number of indents so far
        s_string += "  fact: " + str(s_fact.statement)
        # add one more level of indent for fact and add its statement
        # check is asserted
        if s_fact.asserted:
            s_string += " ASSERTED"
        s_string += "\n"
        # if this fact is supported by something,
        # recursively call helper function on each fact-rule pair in supported by list
        # add 1 to indentation to make sure it is updated since we added in front of "fact: " above
        if len(s_fact.supported_by) > 0:
            for support in s_fact.supported_by:
                s_string += self.add_support(support, indent+1)
        # almost the same logic for rule
        # only the lhs, rhs is different (similar to main function)
        for i in range(indent):
                s_string += "  "
        s_string += "  rule: ("
        s_string += str(s_rule.lhs[0])
        for left in s_rule.lhs[1:]:
            s_string += ", " + str(left)
        s_string += ") -> " + str(s_rule.rhs)
        if s_rule.asserted:
            s_string += " ASSERTED"
        s_string += "\n"
        if len(s_rule.supported_by) > 0:
            for support in s_rule.supported_by:
                s_string += self.add_support(support, indent+1)
        # return the resulting string in order to then append this to the main string from the main function
        return s_string


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment
