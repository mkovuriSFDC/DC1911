/**
 * Northpeak Outfitters - Customer 360 service for the Northpeak Store Assistant agent.
 * Reads unified profiles, calculated insights and engagement data from Data Cloud.
 */
public with sharing class NP_CustomerProfileService {

    // ---- Data Cloud object names ----
    public static final String UNIFIED = 'UnifiedssotIndividualNpcu__dlm';
    public static final String LINK = 'UnifiedLinkssotIndividualNpcu__dlm';
    public static final String LTV = 'NP_Customer_LTV__cio';
    public static final String WEB = 'NP_Web_Engagement__cio';
    public static final String ORDERS = 'NP_Order__dlm';
    public static final String EVENTS = 'NP_Web_Event__dlm';
    public static final String LOYALTY = 'NP_Loyalty_Member__dlm';

    public static final Decimal AT_RISK_MIN_SPEND = 1500;

    // ---- Query abstraction (mockable in tests) ----
    public interface Query {
        List<Map<String, Object>> run(String sql);
    }

    public class CdpQueryImpl implements Query {
        public List<Map<String, Object>> run(String sql) {
            ConnectApi.CdpQueryInput input = new ConnectApi.CdpQueryInput();
            input.sql = sql;
            ConnectApi.CdpQueryOutputV2 output = ConnectApi.CdpQuery.queryAnsiSqlV2(input);
            List<String> cols = columnOrder(JSON.serialize(output.metadata));
            List<List<Object>> rows = new List<List<Object>>();
            if (output.data != null) {
                for (ConnectApi.CdpQueryV2Row row : output.data) {
                    rows.add(row.rowData);
                }
            }
            return toMaps(cols, rows);
        }
    }

    @TestVisible static Query q = new CdpQueryImpl();

    /** Column names ordered by placeInOrder from serialized query metadata. */
    @TestVisible static List<String> columnOrder(String metadataJson) {
        Map<Integer, String> byOrder = new Map<Integer, String>();
        if (String.isNotBlank(metadataJson) && metadataJson != 'null') {
            Map<String, Object> meta = (Map<String, Object>) JSON.deserializeUntyped(metadataJson);
            Integer fallback = 0;
            for (String col : meta.keySet()) {
                Map<String, Object> m = (Map<String, Object>) meta.get(col);
                Object o = m == null ? null : m.get('placeInOrder');
                byOrder.put(o == null ? fallback : Integer.valueOf(String.valueOf(o)), col);
                fallback++;
            }
        }
        List<Integer> keys = new List<Integer>(byOrder.keySet());
        keys.sort();
        List<String> cols = new List<String>();
        for (Integer k : keys) cols.add(byOrder.get(k));
        return cols;
    }

    @TestVisible static List<Map<String, Object>> toMaps(List<String> cols, List<List<Object>> rows) {
        List<Map<String, Object>> out = new List<Map<String, Object>>();
        for (List<Object> r : rows) {
            Map<String, Object> m = new Map<String, Object>();
            for (Integer i = 0; i < cols.size() && i < r.size(); i++) m.put(cols[i], r[i]);
            out.add(m);
        }
        return out;
    }

    // ---- Helpers ----
    @TestVisible static String esc(String s) { return s == null ? '' : s.replace('\\', '').replace('\'', '\'\''); }
    @TestVisible static String str(Object o) { return o == null ? '' : String.valueOf(o).trim(); }
    @TestVisible static Decimal num(Object o) {
        if (o == null) return 0;
        try { return Decimal.valueOf(String.valueOf(o)); } catch (Exception e) { return 0; }
    }
    @TestVisible static String day(Object o) { String s = str(o); return s.length() >= 10 ? s.substring(0, 10) : s; }
    @TestVisible static String money(Decimal d) { return '$' + d.setScale(0).format(); }
    static String inList(Set<String> vals) {
        List<String> parts = new List<String>();
        for (String v : vals) parts.add('\'' + esc(v) + '\'');
        return String.join(parts, ',');
    }
    @TestVisible static String normalizePhone(String raw) {
        String digits = raw == null ? '' : raw.replaceAll('[^0-9]', '');
        if (digits.length() == 10) return '+1' + digits;
        if (digits.length() == 11 && digits.startsWith('1')) return '+' + digits;
        return digits.length() >= 7 ? '+' + digits : null;
    }
    public static String ltvBand(Decimal score) {
        if (score >= 60) return 'Platinum';
        if (score >= 30) return 'Gold';
        if (score >= 10) return 'Silver';
        return 'Bronze';
    }
    public static String webBand(Decimal score) {
        if (score >= 60) return 'High';
        if (score >= 20) return 'Medium';
        if (score > 0) return 'Low';
        return 'None';
    }

    // ---- Resolution ----
    public class Resolution {
        public List<String> unifiedIds = new List<String>();
        public String message;
    }

    /** Resolve an email / phone / ECOM- / LOY- id / name to unified individual ids. */
    public static Resolution resolve(String searchTerm) {
        Resolution res = new Resolution();
        String term = str(searchTerm);
        if (String.isBlank(term)) { res.message = 'Please provide an email, phone number, Summit Club number or full name.'; return res; }
        Set<String> sourceIds = new Set<String>();
        String upper = term.toUpperCase();
        if (upper.startsWith('ECOM-') || upper.startsWith('LOY-')) {
            sourceIds.add(upper);
        } else if (term.contains('@')) {
            for (Map<String, Object> r : q.run('SELECT ssot__PartyId__c FROM ssot__ContactPointEmail__dlm WHERE LOWER(ssot__EmailAddress__c) LIKE \'%' + esc(term.toLowerCase()) + '%\' LIMIT 20')) {
                sourceIds.add(str(r.get('ssot__PartyId__c')));
            }
        } else if (term.replaceAll('[^0-9]', '').length() >= 7) {
            String p = esc(normalizePhone(term));
            for (Map<String, Object> r : q.run('SELECT ssot__PartyId__c FROM ssot__ContactPointPhone__dlm WHERE ssot__TelephoneNumber__c = \'' + p + '\' OR ssot__FormattedE164PhoneNumber__c = \'' + p + '\' LIMIT 20')) {
                sourceIds.add(str(r.get('ssot__PartyId__c')));
            }
        } else {
            List<String> parts = term.toLowerCase().split('\\s+');
            String cond = parts.size() >= 2
                ? 'LOWER(ssot__FirstName__c) = \'' + esc(parts[0]) + '\' AND LOWER(ssot__LastName__c) = \'' + esc(parts[parts.size() - 1]) + '\''
                : 'LOWER(ssot__LastName__c) = \'' + esc(parts[0]) + '\'';
            for (Map<String, Object> r : q.run('SELECT ssot__Id__c FROM ssot__Individual__dlm WHERE ' + cond + ' LIMIT 20')) {
                sourceIds.add(str(r.get('ssot__Id__c')));
            }
        }
        sourceIds.remove('');
        if (sourceIds.isEmpty()) { res.message = 'No Northpeak customer found for "' + term + '".'; return res; }
        Set<String> uids = new Set<String>();
        for (Map<String, Object> r : q.run('SELECT UnifiedRecordId__c FROM ' + LINK + ' WHERE SourceRecordId__c IN (' + inList(sourceIds) + ')')) {
            uids.add(str(r.get('UnifiedRecordId__c')));
        }
        uids.remove('');
        res.unifiedIds.addAll(uids);
        if (uids.isEmpty()) res.message = 'Customer records were found but are not unified yet. Please try again later.';
        return res;
    }

    // ---- Profile ----
    public class Profile {
        public String unifiedId, firstName = '', lastName = '', email = '', phone = '', city = '';
        public Set<String> crmIds = new Set<String>(), ecomIds = new Set<String>(), loyIds = new Set<String>();
        public String tier = '', homeStore = '';
        public Decimal points = 0, spend = 0, orders = 0, orders180 = 0, ltvScore = 0, webScore = 0, events30 = 0, sessions = 0;
        public String lastOrder = '', lastVisit = '';
        public List<String> recentOrders = new List<String>();
        public List<String> topCategories = new List<String>();
        public Set<String> boughtCodes = new Set<String>(), boughtCategories = new Set<String>();
        public Boolean atRisk = false;
    }

    public static Profile load(String unifiedId) {
        Profile p = new Profile();
        p.unifiedId = unifiedId;
        String uid = esc(unifiedId);
        for (Map<String, Object> r : q.run('SELECT ssot__FirstName__c, ssot__LastName__c FROM ' + UNIFIED + ' WHERE ssot__Id__c = \'' + uid + '\' LIMIT 1')) {
            p.firstName = str(r.get('ssot__FirstName__c')); p.lastName = str(r.get('ssot__LastName__c'));
        }
        Set<String> all = new Set<String>();
        for (Map<String, Object> r : q.run('SELECT SourceRecordId__c FROM ' + LINK + ' WHERE UnifiedRecordId__c = \'' + uid + '\'')) {
            String sid = str(r.get('SourceRecordId__c'));
            if (String.isBlank(sid)) continue;
            all.add(sid);
            if (sid.startsWith('ECOM-')) p.ecomIds.add(sid);
            else if (sid.startsWith('LOY-')) p.loyIds.add(sid);
            else if (sid.startsWith('003')) p.crmIds.add(sid);
        }
        if (!all.isEmpty()) {
            for (Map<String, Object> r : q.run('SELECT ssot__EmailAddress__c FROM ssot__ContactPointEmail__dlm WHERE ssot__PartyId__c IN (' + inList(all) + ') LIMIT 5')) {
                if (String.isBlank(p.email)) p.email = str(r.get('ssot__EmailAddress__c')).toLowerCase();
            }
            for (Map<String, Object> r : q.run('SELECT ssot__TelephoneNumber__c FROM ssot__ContactPointPhone__dlm WHERE ssot__PartyId__c IN (' + inList(all) + ') LIMIT 5')) {
                if (String.isBlank(p.phone)) p.phone = str(r.get('ssot__TelephoneNumber__c'));
            }
        }
        if (!p.crmIds.isEmpty()) {
            for (Contact c : [SELECT MailingCity, MailingState FROM Contact WHERE Id IN :p.crmIds LIMIT 1]) {
                p.city = (c.MailingCity == null ? '' : c.MailingCity) + (c.MailingState == null ? '' : ', ' + c.MailingState);
            }
        }
        if (!p.loyIds.isEmpty()) {
            for (Map<String, Object> r : q.run('SELECT Tier__c, PointsBalance__c, HomeStoreId__c FROM ' + LOYALTY + ' WHERE MemberId__c IN (' + inList(p.loyIds) + ') LIMIT 1')) {
                p.tier = str(r.get('Tier__c')); p.points = num(r.get('PointsBalance__c')); p.homeStore = str(r.get('HomeStoreId__c'));
            }
        }
        for (Map<String, Object> r : q.run('SELECT LifetimeSpend__c, OrderCount__c, LastOrderDate__c, Orders180d__c, LtvScore__c FROM ' + LTV + ' WHERE UnifiedIndividualId__c = \'' + uid + '\' LIMIT 1')) {
            p.spend = num(r.get('LifetimeSpend__c')); p.orders = num(r.get('OrderCount__c')); p.lastOrder = day(r.get('LastOrderDate__c'));
            p.orders180 = num(r.get('Orders180d__c')); p.ltvScore = num(r.get('LtvScore__c'));
        }
        for (Map<String, Object> r : q.run('SELECT WebEngagementScore__c, Events30d__c, SessionCount__c, LastWebVisit__c FROM ' + WEB + ' WHERE UnifiedIndividualId__c = \'' + uid + '\' LIMIT 1')) {
            p.webScore = num(r.get('WebEngagementScore__c')); p.events30 = num(r.get('Events30d__c'));
            p.sessions = num(r.get('SessionCount__c')); p.lastVisit = day(r.get('LastWebVisit__c'));
        }
        if (!p.ecomIds.isEmpty()) {
            String ids = inList(p.ecomIds);
            Integer n = 0;
            for (Map<String, Object> r : q.run('SELECT OrderDate__c, OrderTotal__c, PrimaryCategory__c, Channel__c, StoreId__c, ProductCode__c FROM ' + ORDERS + ' WHERE CustomerId__c IN (' + ids + ') ORDER BY OrderDate__c DESC LIMIT 50')) {
                p.boughtCodes.add(str(r.get('ProductCode__c')));
                p.boughtCategories.add(str(r.get('PrimaryCategory__c')));
                if (n++ < 3) {
                    String ch = str(r.get('Channel__c')) == 'Web' ? 'online' : 'in store ' + str(r.get('StoreId__c'));
                    p.recentOrders.add(day(r.get('OrderDate__c')) + ': ' + money(num(r.get('OrderTotal__c'))) + ' ' + str(r.get('PrimaryCategory__c')) + ' (' + ch + ')');
                }
            }
            for (Map<String, Object> r : q.run('SELECT Category__c, SUM(Weight__c) AS w FROM ' + EVENTS + ' WHERE CustomerId__c IN (' + ids + ') GROUP BY Category__c ORDER BY w DESC LIMIT 3')) {
                p.topCategories.add(str(r.get('Category__c')));
            }
        }
        p.atRisk = p.spend >= AT_RISK_MIN_SPEND && p.orders180 == 0 && p.events30 <= 2;
        return p;
    }

    public static String summarize(Profile p) {
        List<String> l = new List<String>();
        l.add('CUSTOMER: ' + (p.firstName + ' ' + p.lastName).trim() + (String.isBlank(p.city) ? '' : ' (' + p.city + ')'));
        l.add('Contact: ' + (String.isBlank(p.email) ? 'no email' : p.email) + ' | ' + (String.isBlank(p.phone) ? 'no phone' : p.phone));
        List<String> src = new List<String>();
        if (!p.crmIds.isEmpty()) src.add('CRM contact');
        if (!p.ecomIds.isEmpty()) src.add('webshop ' + String.join(new List<String>(p.ecomIds), '/'));
        if (!p.loyIds.isEmpty()) src.add('Summit Club ' + String.join(new List<String>(p.loyIds), '/'));
        l.add('Unified from ' + src.size() + ' source record(s): ' + String.join(src, ', '));
        l.add('Summit Club: ' + (String.isBlank(p.tier) ? 'not a member (invite them to join)' : p.tier + ' tier, ' + p.points.setScale(0).format() + ' points, home store ' + p.homeStore));
        l.add('Lifetime value: ' + ltvBand(p.ltvScore) + ' (score ' + p.ltvScore.setScale(0) + ') - ' + money(p.spend) + ' over ' + p.orders.setScale(0) + ' orders' + (String.isBlank(p.lastOrder) ? '' : ', last order ' + p.lastOrder));
        l.add('Web engagement: ' + webBand(p.webScore) + ' (score ' + p.webScore.setScale(0) + ', ' + p.events30.setScale(0) + ' events in last 30 days' + (String.isBlank(p.lastVisit) ? '' : ', last visit ' + p.lastVisit) + ')');
        if (!p.topCategories.isEmpty()) l.add('Most browsed: ' + String.join(p.topCategories, ', '));
        if (!p.recentOrders.isEmpty()) l.add('Recent orders: ' + String.join(p.recentOrders, '; '));
        l.add(p.atRisk ? 'ALERT: HIGH-VALUE AT RISK - big past spender with no purchase in 6 months. Prioritise a warm welcome-back.' : 'Status: active / not at risk');
        return String.join(l, '\n');
    }

    // ---- Recommendations ----
    static final Map<String, String> COMPLEMENT = new Map<String, String>{
        'Tents' => 'Sleeping Bags', 'Sleeping Bags' => 'Tents', 'Backpacks' => 'Camp Kitchen', 'Footwear' => 'Trail Running',
        'Jackets' => 'Backpacks', 'Climbing' => 'Footwear', 'Camp Kitchen' => 'Tents', 'Trail Running' => 'Jackets'
    };

    public static String recommend(String unifiedId) {
        if (String.isBlank(unifiedId)) return 'No customer identified yet - look the customer up first.';
        Profile p = load(unifiedId);
        List<String> cats = new List<String>();
        for (String c : p.topCategories) if (!p.boughtCategories.contains(c) && !cats.contains(c)) cats.add(c);
        for (String c : p.topCategories) if (!cats.contains(c)) cats.add(c);
        Map<String, String> compSource = new Map<String, String>();
        for (String c : p.boughtCategories) {
            String comp = COMPLEMENT.get(c);
            if (comp != null && !cats.contains(comp)) { cats.add(comp); compSource.put(comp, c); }
        }
        if (cats.isEmpty()) cats.addAll(new List<String>{ 'Jackets', 'Footwear', 'Backpacks' });
        Boolean premium = p.ltvScore >= 30 || p.tier == 'Summit';
        Map<String, List<PricebookEntry>> byCat = new Map<String, List<PricebookEntry>>();
        for (PricebookEntry e : [SELECT Product2.Name, Product2.ProductCode, Product2.Family, UnitPrice FROM PricebookEntry
                                 WHERE Pricebook2.IsStandard = true AND IsActive = true AND Product2.IsActive = true
                                 AND Product2.ProductCode LIKE 'NP-%' AND Product2.Family IN :cats ORDER BY UnitPrice DESC]) {
            if (p.boughtCodes.contains(e.Product2.ProductCode)) continue;
            if (!byCat.containsKey(e.Product2.Family)) byCat.put(e.Product2.Family, new List<PricebookEntry>());
            byCat.get(e.Product2.Family).add(e);
        }
        List<String> recs = new List<String>();
        for (String c : cats) {
            if (recs.size() >= 3) break;
            List<PricebookEntry> opts = byCat.get(c);
            if (opts == null || opts.isEmpty()) continue;
            PricebookEntry pick = premium ? opts[0] : opts[Math.min(opts.size() - 1, opts.size() / 2)];
            String why = p.topCategories.contains(c) && !p.boughtCategories.contains(c) ? 'browsed ' + c + ' online but has not bought yet'
                       : p.topCategories.contains(c) ? 'keeps coming back to ' + c + ' online'
                       : compSource.containsKey(c) ? 'pairs well with their past ' + compSource.get(c) + ' purchases'
                       : 'a natural next step from their recent ' + c + ' purchases';
            recs.add((recs.size() + 1) + '. ' + pick.Product2.Name + ' (' + pick.Product2.ProductCode + ', ' + money(pick.UnitPrice) + ') - ' + why);
        }
        if (recs.isEmpty()) recs.add('No catalog matches found - suggest the current seasonal bestsellers.');
        String name = (p.firstName + ' ' + p.lastName).trim();
        List<String> l = new List<String>{ 'RECOMMENDATIONS FOR ' + name + ':' };
        l.addAll(recs);
        if (p.tier == 'Summit') l.add('Perk: Summit members get free tent pitching/boot fitting and 2x points this month.');
        else if (p.tier == 'Trailblazer') l.add('Perk: Trailblazer members are on the way to Summit tier - mention free fittings and 2x points once they upgrade.');
        else if (p.tier == 'Base Camp') l.add('Perk: remind them Base Camp members earn 10 points per dollar.');
        else l.add('Talking point: not in Summit Club - offer to enrol today for 500 welcome points.');
        if (p.atRisk) l.add('Win-back: this customer is HIGH-VALUE AT RISK - offer the 20% welcome-back voucher (code COMEBACK20) on today\'s purchase.');
        return String.join(l, '\n');
    }
}
