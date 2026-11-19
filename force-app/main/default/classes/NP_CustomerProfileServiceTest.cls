@isTest
private class NP_CustomerProfileServiceTest {

    /** Mock Data Cloud query: returns canned rows based on the table referenced in the SQL. */
    private class MockQuery implements NP_CustomerProfileService.Query {
        Boolean multi = false;
        Boolean empty = false;
        Boolean atRisk = true;
        MockQuery(Boolean multi, Boolean empty, Boolean atRisk) { this.multi = multi; this.empty = empty; this.atRisk = atRisk; }
        public List<Map<String, Object>> run(String sql) {
            if (empty) return new List<Map<String, Object>>();
            if (sql.contains('FROM ssot__ContactPointEmail__dlm WHERE LOWER')) return rows('ssot__PartyId__c', 'ECOM-10001');
            if (sql.contains('FROM ssot__ContactPointPhone__dlm WHERE ssot__TelephoneNumber__c')) return rows('ssot__PartyId__c', 'LOY-50001');
            if (sql.contains('FROM ssot__Individual__dlm')) return rows('ssot__Id__c', 'ECOM-10001');
            if (sql.contains('SELECT UnifiedRecordId__c')) {
                List<Map<String, Object>> r = rows('UnifiedRecordId__c', 'U1');
                if (multi) r.addAll(rows('UnifiedRecordId__c', 'U2'));
                return r;
            }
            if (sql.contains('SELECT SourceRecordId__c')) {
                List<Map<String, Object>> r = rows('SourceRecordId__c', 'ECOM-10001');
                r.addAll(rows('SourceRecordId__c', 'LOY-50001'));
                r.addAll(rows('SourceRecordId__c', '003000000000001AAA'));
                return r;
            }
            if (sql.contains('FROM ' + NP_CustomerProfileService.UNIFIED)) return new List<Map<String, Object>>{ new Map<String, Object>{ 'ssot__FirstName__c' => 'Jane', 'ssot__LastName__c' => 'Doe' } };
            if (sql.contains('SELECT ssot__EmailAddress__c')) return rows('ssot__EmailAddress__c', ' Jane.Doe@Example.com ');
            if (sql.contains('SELECT ssot__TelephoneNumber__c')) return rows('ssot__TelephoneNumber__c', '+13035550142');
            if (sql.contains('FROM ' + NP_CustomerProfileService.LOYALTY)) return new List<Map<String, Object>>{ new Map<String, Object>{ 'Tier__c' => 'Summit', 'PointsBalance__c' => 4200, 'HomeStoreId__c' => 'NP-S01' } };
            if (sql.contains('FROM ' + NP_CustomerProfileService.LTV)) return new List<Map<String, Object>>{ new Map<String, Object>{
                'LifetimeSpend__c' => 2350.5, 'OrderCount__c' => 7, 'LastOrderDate__c' => '2026-04-12T10:00:00.000Z', 'Orders180d__c' => atRisk ? 0 : 2, 'LtvScore__c' => 45 } };
            if (sql.contains('FROM ' + NP_CustomerProfileService.WEB)) return new List<Map<String, Object>>{ new Map<String, Object>{
                'WebEngagementScore__c' => '12.5', 'Events30d__c' => 0, 'SessionCount__c' => 3, 'LastWebVisit__c' => '2026-03-01T10:00:00.000Z' } };
            if (sql.contains('FROM ' + NP_CustomerProfileService.ORDERS)) return new List<Map<String, Object>>{
                new Map<String, Object>{ 'OrderDate__c' => '2026-04-12T10:00:00Z', 'OrderTotal__c' => 389, 'PrimaryCategory__c' => 'Tents', 'Channel__c' => 'Web', 'StoreId__c' => 'WEB', 'ProductCode__c' => 'NP-001' },
                new Map<String, Object>{ 'OrderDate__c' => '2026-02-01T10:00:00Z', 'OrderTotal__c' => 229, 'PrimaryCategory__c' => 'Footwear', 'Channel__c' => 'Store', 'StoreId__c' => 'NP-S01', 'ProductCode__c' => 'NP-016' } };
            if (sql.contains('FROM ' + NP_CustomerProfileService.EVENTS)) return new List<Map<String, Object>>{
                new Map<String, Object>{ 'Category__c' => 'Jackets', 'w' => 20 }, new Map<String, Object>{ 'Category__c' => 'Tents', 'w' => 10 } };
            return new List<Map<String, Object>>();
        }
        List<Map<String, Object>> rows(String col, Object val) {
            return new List<Map<String, Object>>{ new Map<String, Object>{ col => val } };
        }
    }

    @testSetup static void setup() {
        Id pb = Test.getStandardPricebookId();
        List<Product2> prods = new List<Product2>{
            new Product2(Name = 'Stormshell 3L Rain Jacket', ProductCode = 'NP-021', Family = 'Jackets', IsActive = true),
            new Product2(Name = 'Switchback Fleece Hoodie', ProductCode = 'NP-023', Family = 'Jackets', IsActive = true),
            new Product2(Name = 'Glacier Down Bag', ProductCode = 'NP-006', Family = 'Sleeping Bags', IsActive = true),
            new Product2(Name = 'Skyline Trail Shoe', ProductCode = 'NP-036', Family = 'Trail Running', IsActive = true),
            new Product2(Name = 'Ridgeline 2P Tent', ProductCode = 'NP-001', Family = 'Tents', IsActive = true)
        };
        insert prods;
        List<PricebookEntry> pbes = new List<PricebookEntry>();
        Decimal price = 100;
        for (Product2 p : prods) { pbes.add(new PricebookEntry(Pricebook2Id = pb, Product2Id = p.Id, UnitPrice = price, IsActive = true)); price += 50; }
        insert pbes;
    }

    @isTest static void profileByEmailAtRisk() {
        NP_CustomerProfileService.q = new MockQuery(false, false, true);
        NP_GetCustomerProfile.Input i = new NP_GetCustomerProfile.Input();
        i.searchTerm = 'jane.doe@example.com';
        Test.startTest();
        List<NP_GetCustomerProfile.Output> o = NP_GetCustomerProfile.run(new List<NP_GetCustomerProfile.Input>{ i });
        Test.stopTest();
        System.assertEquals('U1', o[0].unifiedId);
        System.assert(o[0].profileSummary.contains('Jane Doe'), o[0].profileSummary);
        System.assert(o[0].profileSummary.contains('HIGH-VALUE AT RISK'), o[0].profileSummary);
        System.assert(o[0].profileSummary.contains('Summit'), o[0].profileSummary);
    }

    @isTest static void profileByPhoneAndIdsAndName() {
        NP_CustomerProfileService.q = new MockQuery(false, false, false);
        for (String term : new List<String>{ '(303) 555-0142', 'LOY-50001', 'Jane Doe', 'Doe' }) {
            NP_CustomerProfileService.Resolution r = NP_CustomerProfileService.resolve(term);
            System.assertEquals(1, r.unifiedIds.size(), term);
        }
        NP_CustomerProfileService.Profile p = NP_CustomerProfileService.load('U1');
        System.assertEquals(false, p.atRisk);
        System.assert(NP_CustomerProfileService.summarize(p).contains('not at risk'));
    }

    @isTest static void multipleMatches() {
        NP_CustomerProfileService.q = new MockQuery(true, false, false);
        NP_GetCustomerProfile.Input i = new NP_GetCustomerProfile.Input();
        i.searchTerm = 'Jane Doe';
        List<NP_GetCustomerProfile.Output> o = NP_GetCustomerProfile.run(new List<NP_GetCustomerProfile.Input>{ i });
        System.assert(o[0].profileSummary.contains('Several customers'), o[0].profileSummary);
    }

    @isTest static void notFoundAndBlank() {
        NP_CustomerProfileService.q = new MockQuery(false, true, false);
        NP_GetCustomerProfile.Input i = new NP_GetCustomerProfile.Input();
        i.searchTerm = 'nobody@example.com';
        System.assert(NP_GetCustomerProfile.run(new List<NP_GetCustomerProfile.Input>{ i })[0].profileSummary.contains('No Northpeak customer'));
        System.assert(NP_CustomerProfileService.resolve('  ').message.contains('Please provide'));
        System.assert(NP_CustomerProfileService.recommend('').contains('look the customer up'));
    }

    @isTest static void recommendations() {
        NP_CustomerProfileService.q = new MockQuery(false, false, true);
        NP_GetRecommendations.Input i = new NP_GetRecommendations.Input();
        i.unifiedId = 'U1';
        List<NP_GetRecommendations.Output> o = NP_GetRecommendations.run(new List<NP_GetRecommendations.Input>{ i });
        System.assert(o[0].recommendations.contains('RECOMMENDATIONS FOR Jane Doe'), o[0].recommendations);
        System.assert(o[0].recommendations.contains('Switchback'), o[0].recommendations);
        System.assert(!o[0].recommendations.contains('NP-001,'), 'already bought product must be excluded');
        System.assert(o[0].recommendations.contains('COMEBACK20'));
    }

    @isTest static void helpersAndParsing() {
        System.assertEquals('Platinum', NP_CustomerProfileService.ltvBand(80));
        System.assertEquals('Gold', NP_CustomerProfileService.ltvBand(40));
        System.assertEquals('Silver', NP_CustomerProfileService.ltvBand(15));
        System.assertEquals('Bronze', NP_CustomerProfileService.ltvBand(1));
        System.assertEquals('High', NP_CustomerProfileService.webBand(70));
        System.assertEquals('Medium', NP_CustomerProfileService.webBand(30));
        System.assertEquals('Low', NP_CustomerProfileService.webBand(5));
        System.assertEquals('None', NP_CustomerProfileService.webBand(0));
        System.assertEquals('+13035550142', NP_CustomerProfileService.normalizePhone('303-555-0142'));
        System.assertEquals('+13035550142', NP_CustomerProfileService.normalizePhone('1 303 555 0142'));
        System.assertEquals(null, NP_CustomerProfileService.normalizePhone('12'));
        System.assertEquals(0, NP_CustomerProfileService.num('abc'));
        System.assertEquals('O\'\'Neil', NP_CustomerProfileService.esc('O\'Neil'));
        List<String> cols = NP_CustomerProfileService.columnOrder('{"b":{"placeInOrder":1},"a":{"placeInOrder":0}}');
        System.assertEquals(new List<String>{ 'a', 'b' }, cols);
        List<Map<String, Object>> m = NP_CustomerProfileService.toMaps(cols, new List<List<Object>>{ new List<Object>{ 1, 2 } });
        System.assertEquals(2, m[0].get('b'));
        try {
            new NP_CustomerProfileService.CdpQueryImpl().run('SELECT ssot__Id__c FROM ssot__Individual__dlm LIMIT 1');
        } catch (Exception e) {
            System.assertNotEquals(null, e.getMessage()); // ConnectApi is not available in unit tests
        }
    }

    @isTest static void errorsAreHandled() {
        NP_CustomerProfileService.q = new ThrowingQuery();
        NP_GetCustomerProfile.Input i = new NP_GetCustomerProfile.Input();
        i.searchTerm = 'jane@example.com';
        System.assert(NP_GetCustomerProfile.run(new List<NP_GetCustomerProfile.Input>{ i })[0].profileSummary.contains('lookup failed'));
        NP_GetRecommendations.Input r = new NP_GetRecommendations.Input();
        r.unifiedId = 'U1';
        System.assert(NP_GetRecommendations.run(new List<NP_GetRecommendations.Input>{ r })[0].recommendations.contains('Could not'));
    }

    private class ThrowingQuery implements NP_CustomerProfileService.Query {
        public List<Map<String, Object>> run(String sql) { throw new QueryException('boom'); }
    }
}
