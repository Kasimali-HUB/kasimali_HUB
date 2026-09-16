from app.exceptions.records import PayrollRunRecord
from app.exceptions.schemas import ExceptionPayload
from app.exceptions.service import build_exception_queue, flagged_only

SECRET = "test-secret"


def _record(employee_id="emp-1", name="Jane Doe", gross=50_000, actual_net=None):
    # Default actual_net close to what the engine would produce, so tests
    # can override it to force a flag.
    return PayrollRunRecord(
        employee_id=employee_id,
        employee_name=name,
        annual_gross_salary=gross,
        actual_net_salary=actual_net if actual_net is not None else 39_140.33,
    )


def test_payload_never_contains_a_name_or_employee_id():
    # Structural check: ExceptionPayload's own fields can't hold PII,
    # regardless of what's fed in - this test documents and locks that in.
    payload_fields = set(ExceptionPayload.model_fields.keys())
    assert "employee_name" not in payload_fields
    assert "employee_id" not in payload_fields
    assert "name" not in payload_fields


def test_matching_actual_and_expected_net_is_not_flagged():
    records = [_record(actual_net=39_140.33)]
    payloads, _ = build_exception_queue(
        records, run_id="run-1", pseudonymization_secret=SECRET
    )
    assert payloads[0].flagged is False


def test_large_variance_is_flagged():
    records = [_record(actual_net=39_140.33 * 1.20)]  # +20%, well above tolerance
    payloads, _ = build_exception_queue(
        records, run_id="run-1", pseudonymization_secret=SECRET
    )
    assert payloads[0].flagged is True


def test_token_map_lets_associate_resolve_flagged_employee_locally():
    records = [_record(employee_id="emp-42", actual_net=39_140.33 * 1.5)]
    payloads, token_map = build_exception_queue(
        records, run_id="run-1", pseudonymization_secret=SECRET
    )
    token = payloads[0].employee_token
    assert token_map[token] == "emp-42"


def test_flagged_only_filters_correctly():
    records = [
        _record(employee_id="emp-1", actual_net=39_140.33),  # matches, not flagged
        _record(employee_id="emp-2", actual_net=39_140.33 * 1.3),  # flagged
    ]
    payloads, _ = build_exception_queue(
        records, run_id="run-1", pseudonymization_secret=SECRET
    )
    result = flagged_only(payloads)
    assert len(result) == 1
    assert result[0].flagged is True
