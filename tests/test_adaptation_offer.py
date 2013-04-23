""" Test the adaptation offers. """


import sys
import unittest

from apptools.adaptation.adaptation_offer import AdaptationOffer


class TestAdaptationOffer(unittest.TestCase):
    """ Test the adaptation offers. """

    def test_lazy_loading(self):

        LAZY_EXAMPLES = 'apptools.adaptation.tests.lazy_examples'
        if LAZY_EXAMPLES in sys.modules:
            del sys.modules[LAZY_EXAMPLES]

        offer = AdaptationOffer(
            factory       =(LAZY_EXAMPLES + '.IBarToIFoo'),
            from_protocol =(LAZY_EXAMPLES + '.IBar'),
            to_protocol   =(LAZY_EXAMPLES + '.IFoo'),
        )

        self.assertNotIn(LAZY_EXAMPLES, sys.modules)

        factory = offer.factory

        self.assertIn(LAZY_EXAMPLES, sys.modules)

        from apptools.adaptation.tests.lazy_examples import IBarToIFoo
        self.assertIs(factory, IBarToIFoo)


        del sys.modules[LAZY_EXAMPLES]

        from_protocol = offer.from_protocol

        from apptools.adaptation.tests.lazy_examples import IBar
        self.assertIs(from_protocol, IBar)


        del sys.modules[LAZY_EXAMPLES]

        to_protocol = offer.to_protocol

        from apptools.adaptation.tests.lazy_examples import IFoo
        self.assertIs(to_protocol, IFoo)


if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
