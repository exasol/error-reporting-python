Prepare Test

  $ export ROOT=$TESTDIR/../../

  $ cat > pymodule.py << EOF
  > from exasol import error
  > from exasol.error import Parameter
  > error1 = error.ExaError(
  >   "E-TEST-1",
  >   "this is an error",
  >   ["no mitigation available"],
  >   {"param": Parameter("value", "some description")},
  > )
  > error2 = error.ExaError(
  >   "E-TEST-2", "this is an error", ["no mitigation available"], {"param": "value"}
  > )
  > EOF

Test module entry point

  $ python -m exasol.error --debug parse pymodule.py | python -m json.tool --json-lines
  {
      "identifier": "E-TEST-1",
      "message": "this is an error",
      "messagePlaceholders": [
          {
              "placeholder": "param",
              "description": ""
          }
      ],
      "description": null,
      "internalDescription": null,
      "potentialCauses": null,
      "mitigations": [
          "no mitigation available"
      ],
      "sourceFile": "pymodule.py",
      "sourceLine": 3,
      "contextHash": null
  }
  {
      "identifier": "E-TEST-2",
      "message": "this is an error",
      "messagePlaceholders": [
          {
              "placeholder": "param",
              "description": ""
          }
      ],
      "description": null,
      "internalDescription": null,
      "potentialCauses": null,
      "mitigations": [
          "no mitigation available"
      ],
      "sourceFile": "pymodule.py",
      "sourceLine": 9,
      "contextHash": null
  }

Test cli command

  $ ec --debug parse pymodule.py | python -m json.tool --json-lines
  {
      "identifier": "E-TEST-1",
      "message": "this is an error",
      "messagePlaceholders": [
          {
              "placeholder": "param",
              "description": ""
          }
      ],
      "description": null,
      "internalDescription": null,
      "potentialCauses": null,
      "mitigations": [
          "no mitigation available"
      ],
      "sourceFile": "pymodule.py",
      "sourceLine": 3,
      "contextHash": null
  }
  {
      "identifier": "E-TEST-2",
      "message": "this is an error",
      "messagePlaceholders": [
          {
              "placeholder": "param",
              "description": ""
          }
      ],
      "description": null,
      "internalDescription": null,
      "potentialCauses": null,
      "mitigations": [
          "no mitigation available"
      ],
      "sourceFile": "pymodule.py",
      "sourceLine": 9,
      "contextHash": null
  }
