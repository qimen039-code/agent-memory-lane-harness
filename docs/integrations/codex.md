# Codex Integration

This is a generic Codex reference mapping. Keep `AGENTS.md` at the workspace
root or copy its microkernel into the instruction surface the installed client
actually loads. The host model remains the planner, tool user, recovery owner,
and final-answer author.

## Reference Flow

```text
workspace instruction
-> intake router when a script-verifiable route is needed
-> bounded memory/action context
-> model-owned tool use
-> optional verified current-input correction
-> model-owned verification and final answer
```

Run the model-facing decision controls directly when needed:

```powershell
powershell -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness_intake_router.ps1 `
  -TaskText "<user task>" -Cwd "<workspace root>" `
  -ReceiptMode compact -OutputPath "<workspace root>\.cbh-route.json" | Out-Null
python <HARNESS_ROOT>\harness_action_consumer.py `
  --route-file "<workspace root>\.cbh-route.json" --receipt-mode compact --prompt '<USER_TASK>'
python <HARNESS_ROOT>\behavior_correction_gate.py --list-profiles
```

`behavior_correction_hook.py` is stateless and nonblocking. It may return one
`allow + updatedInput` rewrite only when an accepted deterministic profile
matches and its declared parser/verifier succeeds. No match, ambiguity,
unavailable parser, or any failure leaves the event unchanged. It never grants
authority, denies, freezes, writes memory, or mutates policy.

R5 actions and other sensitive operations still require the exact confirmation
defined by the active instructions and the host's native permission/security
boundary. ACCF does not create a permit or session bypass.

## Update Check

After a Codex client update:

1. confirm the workspace instruction entry still loads;
2. run `validate_policy.ps1` and the router contracts;
3. run `tests/test_nonblocking_runtime_contract.py`;
4. verify the exact installed hook payload and invocation before claiming host
   activation;
5. keep any unsupported surface advisory.

Repository tests prove the reference implementation, not every installed Codex
version or hook lifecycle.
