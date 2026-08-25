
class SourceReliabilityAgent:
    def score(self, source, confidence_from_parser=.5):
        weights={
            "whatsapp_export":.65,
            "whatsapp_live":.65,
            "public_reference":.75,
            "user_realized_sale":.95
        }
        base=weights.get(source,.40)
        return min(.99, .5*base+.5*confidence_from_parser)
