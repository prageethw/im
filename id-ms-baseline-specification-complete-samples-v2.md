Confluence-ready extract based on the finalised ID MS baselines in this thread.

# 1. Scope

_Regenerated for markdown baseline pack alignment. Reference baseline dump: `new-context-working-v24.md`._

- This document consolidates the finalised ID MS baselines for the IntentSpecification domain.

- It covers resource interfaces, hub interfaces, lifecycle and governance rules, concurrency and caching conventions, and the external IntentSpecification event family.

- TMF921 remains the external standards reference. Where shown here, extra headers and HATEOAS links are platform extensions and are intentionally allowed.

# 2. Responsibility and Governance

- ID MS owns the IntentSpecification domain.

- Lifecycle states: DRAFT, ACTIVE, RETIRED.

- Only DRAFT is editable.

- ACTIVE is not mutable or deletable.

- New active versions must start as new DRAFT resources.

- ETag is mandatory on relevant responses.

- If-Match is required on PUT, PATCH, and DELETE where concurrency matters.

- Stale or mismatched ETag returns 412 Precondition Failed with the standard error body.

# 3. Baseline Endpoint Set

| **Area**            | **Method and Path**                                      | **Baseline note**             |
|---------------------|----------------------------------------------------------|-------------------------------|
| IntentSpecification | POST /intentManagement/v5/intentSpecification            | Create resource               |
| IntentSpecification | GET /intentManagement/v5/intentSpecification/{id}        | Retrieve one                  |
| IntentSpecification | GET /intentManagement/v5/intentSpecification             | List with offset/limit        |
| IntentSpecification | PUT /intentManagement/v5/intentSpecification/{id}        | Platform-specific full update |
| IntentSpecification | PATCH /intentManagement/v5/intentSpecification/{id}      | Supported but discouraged     |
| IntentSpecification | DELETE /intentManagement/v5/intentSpecification/{id}     | Delete with If-Match          |
| Hub                 | POST /intentManagement/v5/intentSpecification/hub        | Create EventSubscription      |
| Hub                 | GET /intentManagement/v5/intentSpecification/hub/{id}    | Retrieve EventSubscription    |
| Hub                 | DELETE /intentManagement/v5/intentSpecification/hub/{id} | Delete EventSubscription      |

# 4. Common Transport Rules

- Private caching by default for GET responses.

- Cache bypass allowed via Cache-Control: no-cache.

- Standard stale-write failure pattern uses 412 Precondition Failed.

- Allowed platform extensions include extra headers such as ETag and Cache-Control, and HATEOAS \_links.

# 5. Interface Details

## **POST /intentManagement/v5/intentSpecification**

Creates a new IntentSpecification resource in ID MS. Returns 201 Created, includes mandatory Location and ETag, and returns the full created resource representation with \_links.

**Request**

> POST /intentManagement/v5/intentSpecification HTTP/1.1
>
> Host: mycsp.com.au
>
> Content-Type: application/json
>
> Accept: application/json
>
> Accept-Language: en-AU

**Example request body**

> {
>
> "id": "hospital-surgical-slice-spec-v1.19",
>
> "name": "Hospital-Surgical-Slice-Spec",
>
> "version": "1.19",
>
> "lifecycleStatus": "ACTIVE",
>
> "@type": "IntentSpecification",
>
> "expressionSpecification": {
>
> "@type": "ExpressionSpecification",
>
> "expressionLanguage": "JSON-LD"
>
> }
>
> }

**Response**

> HTTP/1.1 201 Created
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
>
> ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"
>
> Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT
>
> Cache-Control: private, max-age=300

## **GET /intentManagement/v5/intentSpecification/{id}**

Retrieves a single IntentSpecification resource from ID MS by id. Returns 200 OK, includes Content-Location and mandatory ETag, and returns the full resource with \_links.

**Request**

> GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
>
> Host: mycsp.com.au
>
> Accept: application/json
>
> Accept-Language: en-AU

**Response**

> HTTP/1.1 200 OK
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
>
> ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"
>
> Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT
>
> Cache-Control: private, max-age=300

## **GET /intentManagement/v5/intentSpecification**

Lists IntentSpecification resources using offset/limit pagination. Returns 200 OK, includes ETag, X-Total-Count, and X-Result-Count, and uses a top-level array in the lighter list form.

**Request**

> GET /intentManagement/v5/intentSpecification?offset=0&limit=10 HTTP/1.1
>
> Host: mycsp.com.au
>
> Accept: application/json
>
> Accept-Language: en-AU

**Response**

> HTTP/1.1 200 OK
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> ETag: W/"intentSpecification-list-r1"
>
> X-Total-Count: 1
>
> X-Result-Count: 1
>
> Cache-Control: private, max-age=300

## **PUT /intentManagement/v5/intentSpecification/{id}**

Fully replaces an existing IntentSpecification. This is a platform-specific full-update extension. Requires If-Match, returns 200 OK, includes Content-Location and updated ETag, and returns the full updated resource.

**Request**

> PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
>
> Host: mycsp.com.au
>
> Content-Type: application/json
>
> Accept: application/json
>
> Accept-Language: en-AU
>
> If-Match: W/"hospital-surgical-slice-spec-v1.18"

**Response**

> HTTP/1.1 200 OK
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
>
> ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"
>
> Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT
>
> Cache-Control: private, max-age=300
>
> On stale or mismatched ETag:
>
> HTTP/1.1 412 Precondition Failed
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Cache-Control: no-store

## **PATCH /intentManagement/v5/intentSpecification/{id}**

Partially updates an existing IntentSpecification. Supported for compatibility but discouraged in favour of PUT for deterministic full updates. Requires If-Match, returns 200 OK with the full updated resource.

**Request**

> PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
>
> Host: mycsp.com.au
>
> Content-Type: application/json
>
> Accept: application/json
>
> Accept-Language: en-AU
>
> If-Match: W/"hospital-surgical-slice-spec-v1.18"

**Example request body**

> {
>
> "description": "Syntax-first IntentSpecification for hospital surgical slice requests...",
>
> "specCharacteristic": \[
>
> {
>
> "id": "SC-CONTEXT-002",
>
> "name": "priority"
>
> }
>
> \]
>
> }

**Response**

> HTTP/1.1 200 OK
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
>
> ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"
>
> Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT
>
> Cache-Control: private, max-age=300
>
> On stale or mismatched ETag:
>
> HTTP/1.1 412 Precondition Failed
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Cache-Control: no-store

## **DELETE /intentManagement/v5/intentSpecification/{id}**

Deletes an existing IntentSpecification. Requires If-Match, returns 204 No Content on success, and returns 412 Precondition Failed on stale or mismatched ETag.

**Request**

> DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
>
> Host: mycsp.com.au
>
> Accept: application/json
>
> Accept-Language: en-AU
>
> If-Match: W/"hospital-surgical-slice-spec-v1.19-1.19"

**Response**

> HTTP/1.1 204 No Content
>
> On stale or mismatched ETag:
>
> HTTP/1.1 412 Precondition Failed
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Cache-Control: no-store

## **POST /intentManagement/v5/intentSpecification/hub**

Creates a new EventSubscription for IntentSpecification events. Returns 201 Created with Location, ETag, and the created EventSubscription resource.

**Request**

> POST /intentManagement/v5/intentSpecification/hub HTTP/1.1
>
> Host: mycsp.com.au
>
> Content-Type: application/json
>
> Accept: application/json
>
> Accept-Language: en-AU

**Example request body**

> {
>
> "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
>
> "query": "eventType=IntentSpecificationCreateEvent"
>
> }

**Response**

> HTTP/1.1 201 Created
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001
>
> ETag: W/"ESUB-0001-r1"
>
> Cache-Control: private, max-age=300

## **GET /intentManagement/v5/intentSpecification/hub/{id}**

Retrieves an EventSubscription by id. Returns 200 OK with Content-Location and ETag, or 404 Not Found with the standard error body if the subscription does not exist.

**Request**

> GET /intentManagement/v5/intentSpecification/hub/ESUB-0001 HTTP/1.1
>
> Host: mycsp.com.au
>
> Accept: application/json
>
> Accept-Language: en-AU

**Response**

> HTTP/1.1 200 OK
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001
>
> ETag: W/"ESUB-0001-r1"
>
> Cache-Control: private, max-age=300
>
> If missing:
>
> HTTP/1.1 404 Not Found
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Cache-Control: no-store

## **DELETE /intentManagement/v5/intentSpecification/hub/{id}**

Deletes an EventSubscription by id. Requires If-Match, returns 204 No Content on success, and returns 412 Precondition Failed on stale or mismatched ETag.

**Request**

> DELETE /intentManagement/v5/intentSpecification/hub/ESUB-0001 HTTP/1.1
>
> Host: mycsp.com.au
>
> Accept: application/json
>
> Accept-Language: en-AU
>
> If-Match: W/"ESUB-0001-r1"

**Response**

> HTTP/1.1 204 No Content
>
> On stale or mismatched ETag:
>
> HTTP/1.1 412 Precondition Failed
>
> Content-Type: application/json
>
> Content-Language: en-AU
>
> Cache-Control: no-store

# 6. External Event Family

- IntentSpecificationCreateEvent — Emitted when a new IntentSpecification is created.

- IntentSpecificationAttributeValueChangeEvent — Emitted when attribute values on an existing IntentSpecification change.

- IntentSpecificationStatusChangeEvent — Emitted when the lifecycle status of an existing IntentSpecification changes.

- IntentSpecificationDeleteEvent — Emitted when an IntentSpecification is deleted.

**Event envelope notes:**

- TMF-style external event envelope is preserved.

- Event payload carries event.intentSpecification.

- Both reportingSystem and source are kept to stay closer to the TMF-style external event shape.

# 7. Confluence Extraction Notes

- This document is intentionally structured with heading hierarchy and plain code blocks so it can be pasted or imported into Confluence with minimal cleanup.

- If you want, the next pass can convert this into a more Confluence-native style with collapsible sections and shorter examples.

# Appendix A. Complete HTTP and JSON Samples

The following complete samples are included for direct extraction into Confluence. JSON and HTTP blocks use a smaller wrapped code style to reduce page count.

## ID MS interface baseline — POST /intentManagement/v5/intentSpecification

### Summary

Creates a new IntentSpecification resource in ID MS. This is the baselined create operation for the syntax-first surgical hospital slice specification example. It returns 201 Created, includes mandatory Location and ETag headers, and returns the full created resource representation with \_links. The example baseline uses hospital-surgical-slice-spec-v1.19.

### Request headers

POST /intentManagement/v5/intentSpecification HTTP/1.1  
Host: mycsp.com.au  
Content-Type: application/json  
Accept: application/json  
Accept-Language: en-AU

### Request body

{  
"id": "hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",  
"version": "1.19",  
"lifecycleStatus": "ACTIVE",  
"isBundle": false,  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification",  
"@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",  
"validFor": {  
"startDateTime": "2026-04-17T10:00:00+10:00"  
},  
"expressionSpecification": {  
"@type": "ExpressionSpecification",  
"expressionLanguage": "JSON-LD",  
"iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"  
},  
"specCharacteristic": \[  
{  
"id": "SC-DELIVERY-001",  
"name": "slice_type",  
"description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": false,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"isDefault": true,  
"value": "URLLC"  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-001",  
"name": "latency",  
"description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "integer",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "integer",  
"unitOfMeasure": "ms",  
"valueFrom": 0,  
"valueTo": 20,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 10  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-002",  
"name": "availability",  
"description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "number",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "number",  
"unitOfMeasure": "percent",  
"valueFrom": 0,  
"valueTo": 100,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 99.999  
}  
\]  
},  
{  
"id": "SC-CONTEXT-001",  
"name": "geo_location",  
"description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "object",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "object",  
"semanticType": "tio:GeographicSiteRef",  
"referenceModel": "TMF673-Site",  
"requiredFields": \[  
"locationId",  
"locationType",  
"geographicScope"  
\],  
"description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."  
}  
\]  
},  
{  
"id": "SC-CONTEXT-002",  
"name": "priority",  
"description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "CRITICAL",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "HIGH",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "NORMAL",  
"isDefault": true  
}  
\]  
},  
{  
"id": "SC-CONTEXT-003",  
"name": "semantic_tag",  
"description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "medical_urllc_critical",  
"isDefault": true  
}  
\]  
}  
\]  
}

### Response headers

HTTP/1.1 201 Created  
Content-Type: application/json  
Content-Language: en-AU  
Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19  
ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"  
Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT  
Cache-Control: private, max-age=300

### Response body

{  
"id": "hospital-surgical-slice-spec-v1.19",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",  
"version": "1.19",  
"lifecycleStatus": "ACTIVE",  
"isBundle": false,  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification",  
"@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",  
"validFor": {  
"startDateTime": "2026-04-17T10:00:00+10:00"  
},  
"expressionSpecification": {  
"@type": "ExpressionSpecification",  
"expressionLanguage": "JSON-LD",  
"iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"  
},  
"specCharacteristic": \[  
{  
"id": "SC-DELIVERY-001",  
"name": "slice_type",  
"description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": false,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"isDefault": true,  
"value": "URLLC"  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-001",  
"name": "latency",  
"description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "integer",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "integer",  
"unitOfMeasure": "ms",  
"valueFrom": 0,  
"valueTo": 20,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 10  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-002",  
"name": "availability",  
"description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "number",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "number",  
"unitOfMeasure": "percent",  
"valueFrom": 0,  
"valueTo": 100,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 99.999  
}  
\]  
},  
{  
"id": "SC-CONTEXT-001",  
"name": "geo_location",  
"description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "object",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "object",  
"semanticType": "tio:GeographicSiteRef",  
"referenceModel": "TMF673-Site",  
"requiredFields": \[  
"locationId",  
"locationType",  
"geographicScope"  
\],  
"description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."  
}  
\]  
},  
{  
"id": "SC-CONTEXT-002",  
"name": "priority",  
"description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "CRITICAL",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "HIGH",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "NORMAL",  
"isDefault": true  
}  
\]  
},  
{  
"id": "SC-CONTEXT-003",  
"name": "semantic_tag",  
"description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "medical_urllc_critical",  
"isDefault": true  
}  
\]  
}  
\],  
"\_links": {  
"self": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "GET"  
},  
"fullUpdate": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "PUT"  
},  
"partialUpdate": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "PATCH",  
"warning": "PATCH is allowed but discouraged. Use PUT for deterministic specification updates."  
},  
"delete": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "DELETE"  
}  
}  
}

## ID MS interface baseline — PUT /intentManagement/v5/intentSpecification/{id}

### Summary

Fully replaces an existing IntentSpecification resource in ID MS. This is the baselined platform-specific full-update operation. It requires If-Match, returns 200 OK, includes Content-Location and updated ETag, uses private caching by default, and returns the full updated resource with \_links.

### TMF alignment note

This interface is treated as a platform-specific extension:

- TMF core \`IntentSpecification\` model stays aligned

- \`PUT\` full update is our platform extension

- extra platform headers and HATEOAS \`\_links\` are allowed

### Request headers

PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1  
Host: mycsp.com.au  
Content-Type: application/json  
Accept: application/json  
Accept-Language: en-AU  
If-Match: W/"hospital-surgical-slice-spec-v1.18"

### Request body

{  
"id": "hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",  
"version": "1.19",  
"lifecycleStatus": "ACTIVE",  
"isBundle": false,  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification",  
"@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",  
"validFor": {  
"startDateTime": "2026-04-17T10:00:00+10:00"  
},  
"expressionSpecification": {  
"@type": "ExpressionSpecification",  
"expressionLanguage": "JSON-LD",  
"iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"  
},  
"specCharacteristic": \[  
{  
"id": "SC-DELIVERY-001",  
"name": "slice_type",  
"description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": false,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"isDefault": true,  
"value": "URLLC"  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-001",  
"name": "latency",  
"description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "integer",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "integer",  
"unitOfMeasure": "ms",  
"valueFrom": 0,  
"valueTo": 20,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 10  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-002",  
"name": "availability",  
"description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "number",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "number",  
"unitOfMeasure": "percent",  
"valueFrom": 0,  
"valueTo": 100,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 99.999  
}  
\]  
},  
{  
"id": "SC-CONTEXT-001",  
"name": "geo_location",  
"description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "object",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "object",  
"semanticType": "tio:GeographicSiteRef",  
"referenceModel": "TMF673-Site",  
"requiredFields": \[  
"locationId",  
"locationType",  
"geographicScope"  
\],  
"description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."  
}  
\]  
},  
{  
"id": "SC-CONTEXT-002",  
"name": "priority",  
"description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "CRITICAL",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "HIGH",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "NORMAL",  
"isDefault": true  
}  
\]  
},  
{  
"id": "SC-CONTEXT-003",  
"name": "semantic_tag",  
"description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "medical_urllc_critical",  
"isDefault": true  
}  
\]  
}  
\]  
}

### Response headers

HTTP/1.1 200 OK  
Content-Type: application/json  
Content-Language: en-AU  
Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19  
ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"  
Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT  
Cache-Control: private, max-age=300

### Stale or mismatched ETag response headers

HTTP/1.1 412 Precondition Failed  
Content-Type: application/json  
Content-Language: en-AU  
Cache-Control: no-store

### Stale or mismatched ETag response body

{  
"code": "PRECONDITION_FAILED",  
"reason": "ETAG_MISMATCH",  
"message": "The supplied If-Match value does not match the current resource version for 'hospital-surgical-slice-spec-v1.19'.",  
"status": 412,  
"referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",  
"@type": "Error"  
}

### Response body

{  
"id": "hospital-surgical-slice-spec-v1.19",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",  
"version": "1.19",  
"lifecycleStatus": "ACTIVE",  
"isBundle": false,  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification",  
"@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",  
"validFor": {  
"startDateTime": "2026-04-17T10:00:00+10:00"  
},  
"expressionSpecification": {  
"@type": "ExpressionSpecification",  
"expressionLanguage": "JSON-LD",  
"iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"  
},  
"specCharacteristic": \[  
{  
"id": "SC-DELIVERY-001",  
"name": "slice_type",  
"description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": false,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"isDefault": true,  
"value": "URLLC"  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-001",  
"name": "latency",  
"description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "integer",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "integer",  
"unitOfMeasure": "ms",  
"valueFrom": 0,  
"valueTo": 20,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 10  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-002",  
"name": "availability",  
"description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "number",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "number",  
"unitOfMeasure": "percent",  
"valueFrom": 0,  
"valueTo": 100,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 99.999  
}  
\]  
},  
{  
"id": "SC-CONTEXT-001",  
"name": "geo_location",  
"description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "object",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "object",  
"semanticType": "tio:GeographicSiteRef",  
"referenceModel": "TMF673-Site",  
"requiredFields": \[  
"locationId",  
"locationType",  
"geographicScope"  
\],  
"description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."  
}  
\]  
},  
{  
"id": "SC-CONTEXT-002",  
"name": "priority",  
"description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "CRITICAL",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "HIGH",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "NORMAL",  
"isDefault": true  
}  
\]  
},  
{  
"id": "SC-CONTEXT-003",  
"name": "semantic_tag",  
"description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "medical_urllc_critical",  
"isDefault": true  
}  
\]  
}  
\],  
"\_links": {  
"self": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "GET"  
},  
"fullUpdate": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "PUT"  
},  
"partialUpdate": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "PATCH",  
"warning": "PATCH is allowed but discouraged. Use PUT for deterministic specification updates."  
},  
"delete": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "DELETE"  
}  
}  
}

## ID MS interface baseline — PATCH /intentManagement/v5/intentSpecification/{id}

### Summary

Partially updates an existing IntentSpecification resource in ID MS. This is the baselined compatibility partial-update operation. It requires If-Match, returns 200 OK, includes Content-Location and updated ETag, uses private caching by default, and returns the full updated resource with \_links.

### Platform note

This interface is supported, but discouraged in favour of PUT for deterministic full updates.

### TMF alignment note

This interface is treated as TMF-aligned with platform guidance:

- \`PATCH\` exists in the external model

- we add stronger concurrency/caching rules

- we add explicit warning guidance to prefer \`PUT\`

### Request headers

PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1  
Host: mycsp.com.au  
Content-Type: application/json  
Accept: application/json  
Accept-Language: en-AU  
If-Match: W/"hospital-surgical-slice-spec-v1.18"

### Request body

{  
"description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",  
"specCharacteristic": \[  
{  
"id": "SC-CONTEXT-002",  
"name": "priority",  
"description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "CRITICAL",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "HIGH",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "NORMAL",  
"isDefault": true  
}  
\]  
}  
\]  
}

### Response headers

HTTP/1.1 200 OK  
Content-Type: application/json  
Content-Language: en-AU  
Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19  
ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"  
Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT  
Cache-Control: private, max-age=300

### Stale or mismatched ETag response headers

HTTP/1.1 412 Precondition Failed  
Content-Type: application/json  
Content-Language: en-AU  
Cache-Control: no-store

### Stale or mismatched ETag response body

{  
"code": "PRECONDITION_FAILED",  
"reason": "ETAG_MISMATCH",  
"message": "The supplied If-Match value does not match the current resource version for 'hospital-surgical-slice-spec-v1.19'.",  
"status": 412,  
"referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",  
"@type": "Error"  
}

### Response body

{  
"id": "hospital-surgical-slice-spec-v1.19",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",  
"version": "1.19",  
"lifecycleStatus": "ACTIVE",  
"isBundle": false,  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification",  
"@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",  
"validFor": {  
"startDateTime": "2026-04-17T10:00:00+10:00"  
},  
"expressionSpecification": {  
"@type": "ExpressionSpecification",  
"expressionLanguage": "JSON-LD",  
"iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"  
},  
"specCharacteristic": \[  
{  
"id": "SC-DELIVERY-001",  
"name": "slice_type",  
"description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": false,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"isDefault": true,  
"value": "URLLC"  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-001",  
"name": "latency",  
"description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "integer",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "integer",  
"unitOfMeasure": "ms",  
"valueFrom": 0,  
"valueTo": 20,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 10  
}  
\]  
},  
{  
"id": "SC-ASSURANCE-002",  
"name": "availability",  
"description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "number",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "number",  
"unitOfMeasure": "percent",  
"valueFrom": 0,  
"valueTo": 100,  
"rangeInterval": "closed",  
"isDefault": true,  
"value": 99.999  
}  
\]  
},  
{  
"id": "SC-CONTEXT-001",  
"name": "geo_location",  
"description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",  
"valueType": "object",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "object",  
"semanticType": "tio:GeographicSiteRef",  
"referenceModel": "TMF673-Site",  
"requiredFields": \[  
"locationId",  
"locationType",  
"geographicScope"  
\],  
"description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."  
}  
\]  
},  
{  
"id": "SC-CONTEXT-002",  
"name": "priority",  
"description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "CRITICAL",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "HIGH",  
"isDefault": false  
},  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "NORMAL",  
"isDefault": true  
}  
\]  
},  
{  
"id": "SC-CONTEXT-003",  
"name": "semantic_tag",  
"description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",  
"valueType": "string",  
"minCardinality": 1,  
"maxCardinality": 1,  
"configurable": true,  
"@type": "CharacteristicSpecification",  
"characteristicValueSpecification": \[  
{  
"@type": "CharacteristicValueSpecification",  
"valueType": "string",  
"value": "medical_urllc_critical",  
"isDefault": true  
}  
\]  
}  
\],  
"\_links": {  
"self": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "GET"  
},  
"fullUpdate": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "PUT"  
},  
"partialUpdate": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "PATCH",  
"warning": "PATCH is allowed but discouraged. Use PUT for deterministic specification updates."  
},  
"delete": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"method": "DELETE"  
}  
}  
}

## ID MS interface baseline — DELETE /intentManagement/v5/intentSpecification/{id}

### Summary

Deletes an existing IntentSpecification resource in ID MS. This is the baselined delete operation. It requires If-Match, returns 204 No Content on success, and returns 412 Precondition Failed with the standard error body when the ETag is stale or mismatched.

### TMF alignment note

This interface is treated as TMF-aligned with platform concurrency rules:

- core delete route stays aligned

- \`If-Match\` is required by our platform

- stale write protection uses \`412 Precondition Failed\`

### Request headers

DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1  
Host: mycsp.com.au  
Accept: application/json  
Accept-Language: en-AU  
If-Match: W/"hospital-surgical-slice-spec-v1.19-1.19"

### Success response headers

HTTP/1.1 204 No Content

### Stale or mismatched ETag response headers

HTTP/1.1 412 Precondition Failed  
Content-Type: application/json  
Content-Language: en-AU  
Cache-Control: no-store

### Stale or mismatched ETag response body

{  
"code": "PRECONDITION_FAILED",  
"reason": "ETAG_MISMATCH",  
"message": "The supplied If-Match value does not match the current resource version for 'hospital-surgical-slice-spec-v1.19'.",  
"status": 412,  
"referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",  
"@type": "Error"  
}

## ID MS interface baseline — POST /intentManagement/v5/intentSpecification/hub

### Summary

Creates a new EventSubscription in ID MS for IntentSpecification events. This is the baselined hub create operation. It returns 201 Created, includes Location and mandatory ETag, uses the literal subscription style, and returns the created subscription resource with \_links.

### TMF alignment note

This interface is treated as TMF-aligned with platform path and header conventions:

- subscription model remains TMF-style

- we use the domain-owned hub path \`/intentManagement/v5/intentSpecification/hub\`

- extra platform headers such as \`ETag\` and \`Cache-Control\` are allowed

### Subscription style note

- one subscription per event type

- one callback URL per subscription

- \`query\` explicitly filters by \`eventType=...\`

### Request headers

POST /intentManagement/v5/intentSpecification/hub HTTP/1.1  
Host: mycsp.com.au  
Content-Type: application/json  
Accept: application/json  
Accept-Language: en-AU

### Request body

{  
"callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",  
"query": "eventType=IntentSpecificationCreateEvent"  
}

### Response headers

HTTP/1.1 201 Created  
Content-Type: application/json  
Content-Language: en-AU  
Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001  
ETag: W/"ESUB-0001-r1"  
Cache-Control: private, max-age=300

### Response body

{  
"id": "ESUB-0001",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001",  
"callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",  
"query": "eventType=IntentSpecificationCreateEvent",  
"@type": "EventSubscription",  
"\_links": {  
"self": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001",  
"method": "GET"  
},  
"delete": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001",  
"method": "DELETE"  
}  
}  
}

### Other baselined request body variants

{  
"callback": "https://consumer.example.com/listener/intentSpecificationAttributeValueChangeEvent",  
"query": "eventType=IntentSpecificationAttributeValueChangeEvent"  
}

{  
"callback": "https://consumer.example.com/listener/intentSpecificationStatusChangeEvent",  
"query": "eventType=IntentSpecificationStatusChangeEvent"  
}

{  
"callback": "https://consumer.example.com/listener/intentSpecificationDeleteEvent",  
"query": "eventType=IntentSpecificationDeleteEvent"  
}

## ID MS interface baseline — GET /intentManagement/v5/intentSpecification/hub/{id}

### Summary

Retrieves a single EventSubscription resource from ID MS by id. This is the baselined hub retrieve-by-id operation. It returns 200 OK, includes Content-Location and mandatory ETag, uses private caching by default, and returns the subscription resource with \_links.

### TMF alignment note

This interface is treated as TMF-aligned with platform path and header conventions:

- subscription resource model remains TMF-style

- we use the domain-owned hub path \`/intentManagement/v5/intentSpecification/hub/{id}\`

- extra platform headers such as \`ETag\` and \`Cache-Control\` are allowed

### Request headers

GET /intentManagement/v5/intentSpecification/hub/ESUB-0001 HTTP/1.1  
Host: mycsp.com.au  
Accept: application/json  
Accept-Language: en-AU

### Success response headers

HTTP/1.1 200 OK  
Content-Type: application/json  
Content-Language: en-AU  
Content-Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001  
ETag: W/"ESUB-0001-r1"  
Cache-Control: private, max-age=300

### Success response body

{  
"id": "ESUB-0001",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001",  
"callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",  
"query": "eventType=IntentSpecificationCreateEvent",  
"@type": "EventSubscription",  
"\_links": {  
"self": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001",  
"method": "GET"  
},  
"delete": {  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hub/ESUB-0001",  
"method": "DELETE"  
}  
}  
}

### Not found response headers

HTTP/1.1 404 Not Found  
Content-Type: application/json  
Content-Language: en-AU  
Cache-Control: no-store

### Not found response body

{  
"code": "RESOURCE_NOT_FOUND",  
"reason": "NOT_FOUND",  
"message": "No EventSubscription exists for id 'ESUB-0001'.",  
"status": 404,  
"referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",  
"@type": "Error"  
}

## ID MS interface baseline — DELETE /intentManagement/v5/intentSpecification/hub/{id}

### Summary

Deletes an existing EventSubscription resource from ID MS by id. This is the baselined hub delete operation. It requires If-Match, returns 204 No Content on success, and returns 412 Precondition Failed with the standard error body when the ETag is stale or mismatched.

### TMF alignment note

This interface is treated as TMF-aligned with platform path and concurrency conventions:

- subscription delete model remains TMF-style

- we use the domain-owned hub path \`/intentManagement/v5/intentSpecification/hub/{id}\`

- \`If-Match\` is required by our platform

- stale write protection uses \`412 Precondition Failed\`

### Request headers

DELETE /intentManagement/v5/intentSpecification/hub/ESUB-0001 HTTP/1.1  
Host: mycsp.com.au  
Accept: application/json  
Accept-Language: en-AU  
If-Match: W/"ESUB-0001-r1"

### Success response headers

HTTP/1.1 204 No Content

### Stale or mismatched ETag response headers

HTTP/1.1 412 Precondition Failed  
Content-Type: application/json  
Content-Language: en-AU  
Cache-Control: no-store

### Stale or mismatched ETag response body

{  
"code": "PRECONDITION_FAILED",  
"reason": "ETAG_MISMATCH",  
"message": "The supplied If-Match value does not match the current resource version for EventSubscription 'ESUB-0001'.",  
"status": 412,  
"referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",  
"@type": "Error"  
}

## ID MS external event baseline — IntentSpecificationAttributeValueChangeEvent

### Summary

External TMF-aligned event emitted by ID MS when an existing IntentSpecification resource has attribute values updated. This is the baselined attribute-value-change event for the surgical hospital slice specification. It carries event.intentSpecification, and keeps both reportingSystem and source to stay aligned with the TMF-style external event shape.

### TMF alignment note

This event is treated as TMF-aligned with platform-owned concrete content:

- TMF-style external event envelope is preserved

- event payload carries \`event.intentSpecification\`

- concrete field content and example values are platform-owned

### Event JSON

{  
"correlationId": "SPEC-HOSP-SURGICAL-001",  
"description": "IntentSpecificationAttributeValueChangeEvent for update of the surgical hospital slice specification.",  
"eventId": "EVT-SPEC-HOSP-SURGICAL-001-ATTR-0001",  
"eventTime": "2026-04-21T09:00:00+10:00",  
"eventType": "IntentSpecificationAttributeValueChangeEvent",  
"priority": "3",  
"title": "IntentSpecificationAttributeValueChangeEvent",  
"event": {  
"intentSpecification": {  
"id": "hospital-surgical-slice-spec-v1.19",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"description": "Surgical URLLC blueprint for hospital connectivity intents.",  
"version": "1.19",  
"lifecycleStatus": "ACTIVE",  
"lastUpdate": "2026-04-21T09:00:00+10:00",  
"characteristic": \[  
{  
"name": "latency",  
"valueType": "number",  
"configurable": true,  
"description": "Maximum target latency in milliseconds."  
},  
{  
"name": "priority",  
"valueType": "string",  
"configurable": true,  
"description": "Requested service priority."  
},  
{  
"name": "geo_location",  
"valueType": "object",  
"configurable": true,  
"description": "Requested deployment location with locationId, locationType, and geographicScope."  
}  
\],  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification"  
}  
},  
"reportingSystem": {  
"id": "ID-MS",  
"name": "intent-definition-ms",  
"@type": "ReportingResource",  
"@referredType": "LogicalResource"  
},  
"source": {  
"id": "ID-MS",  
"name": "intent-definition-ms",  
"@type": "ReportingResource",  
"@referredType": "LogicalResource"  
},  
"@type": "IntentSpecificationAttributeValueChangeEvent"  
}

## ID MS external event baseline — IntentSpecificationDeleteEvent

### Summary

External TMF-aligned event emitted by ID MS when an IntentSpecification resource is deleted. This is the baselined delete event for the surgical hospital slice specification. It carries a lean event.intentSpecification, and keeps both reportingSystem and source to stay aligned with the TMF-style external event shape.

### TMF alignment note

This event is treated as TMF-aligned with platform-owned concrete content:

- TMF-style external event envelope is preserved

- event payload carries \`event.intentSpecification\`

- concrete field content and example values are platform-owned

### Event JSON

{  
"correlationId": "SPEC-HOSP-SURGICAL-001",  
"description": "IntentSpecificationDeleteEvent for deletion of the surgical hospital slice specification.",  
"eventId": "EVT-SPEC-HOSP-SURGICAL-001-DELETE-0001",  
"eventTime": "2026-04-23T07:00:00+10:00",  
"eventType": "IntentSpecificationDeleteEvent",  
"priority": "3",  
"title": "IntentSpecificationDeleteEvent",  
"event": {  
"intentSpecification": {  
"id": "hospital-surgical-slice-spec-v1.19",  
"href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",  
"name": "Hospital-Surgical-Slice-Spec",  
"@type": "IntentSpecification",  
"@baseType": "EntitySpecification"  
}  
},  
"reportingSystem": {  
"id": "ID-MS",  
"name": "intent-definition-ms",  
"@type": "ReportingResource",  
"@referredType": "LogicalResource"  
},  
"source": {  
"id": "ID-MS",  
"name": "intent-definition-ms",  
"@type": "ReportingResource",  
"@referredType": "LogicalResource"  
},  
"@type": "IntentSpecificationDeleteEvent"  
}
