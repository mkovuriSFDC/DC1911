public with sharing class NP_GetRecommendations {
    public class Input {
        @InvocableVariable(label='Unified Id' description='Unified customer id returned by the profile lookup' required=true)
        public String unifiedId;
    }
    public class Output {
        @InvocableVariable(label='Recommendations' description='Recommended products, perks and talking points')
        public String recommendations;
    }
    @InvocableMethod(label='Northpeak Get Recommendations' description='Recommend Northpeak products and talking points for a unified customer')
    public static List<Output> run(List<Input> inputs) {
        List<Output> outs = new List<Output>();
        for (Input i : inputs) {
            Output o = new Output();
            try {
                o.recommendations = NP_CustomerProfileService.recommend(i.unifiedId);
            } catch (Exception e) {
                o.recommendations = 'Could not build recommendations: ' + e.getMessage();
            }
            outs.add(o);
        }
        return outs;
    }
}