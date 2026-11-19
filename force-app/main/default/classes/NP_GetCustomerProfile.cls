public with sharing class NP_GetCustomerProfile {
    public class Input {
        @InvocableVariable(label='Search Term' description='Customer email, phone, Summit Club number (LOY-), webshop id (ECOM-) or full name' required=true)
        public String searchTerm;
    }
    public class Output {
        @InvocableVariable(label='Profile Summary' description='Unified customer 360 summary')
        public String profileSummary;
        @InvocableVariable(label='Unified Id' description='Unified customer id used for recommendations')
        public String unifiedId;
    }
    @InvocableMethod(label='Northpeak Get Customer Profile' description='Find a Northpeak customer and return their unified 360 profile, value and engagement scores')
    public static List<Output> run(List<Input> inputs) {
        List<Output> outs = new List<Output>();
        for (Input i : inputs) {
            Output o = new Output();
            o.unifiedId = '';
            try {
                NP_CustomerProfileService.Resolution r = NP_CustomerProfileService.resolve(i.searchTerm);
                if (r.unifiedIds.isEmpty()) {
                    o.profileSummary = r.message;
                } else if (r.unifiedIds.size() == 1) {
                    NP_CustomerProfileService.Profile p = NP_CustomerProfileService.load(r.unifiedIds[0]);
                    o.unifiedId = p.unifiedId;
                    o.profileSummary = NP_CustomerProfileService.summarize(p);
                } else {
                    List<String> lines = new List<String>{ 'Several customers match "' + i.searchTerm + '". Ask which one is in the store:' };
                    Integer n = 0;
                    for (String uid : r.unifiedIds) {
                        if (n++ >= 3) break;
                        NP_CustomerProfileService.Profile p = NP_CustomerProfileService.load(uid);
                        lines.add('- ' + (p.firstName + ' ' + p.lastName).trim() + ' | ' + p.email + ' | ' + p.phone + (String.isBlank(p.city) ? '' : ' | ' + p.city));
                    }
                    lines.add('Then look them up again by email or phone.');
                    o.profileSummary = String.join(lines, '\n');
                }
            } catch (Exception e) {
                o.profileSummary = 'Customer lookup failed: ' + e.getMessage();
            }
            outs.add(o);
        }
        return outs;
    }
}