# Setup

1. Clone repo
2. pip install -r requirements.txt

# Launching

`main.py {record_file_name} {-execute|-record} {-time|-time N} {-loop M}`

- `record_file_name` - filename or path to file. In `record` mode file will be created.
- `-record` - create a marco of mouse and keyboard press/release events.
- `-execute` - run a marco.
- `-time`|`-time N`
  - in `record` mode `-time` flag activate recording the time between events
  - in `execute` mode `-time N` indicates how many times faster to play the macro. If `N` is `0`, times faster = infinity 
- `-loop M`.
  - in `execute` mode indicates how many times repeat marco. If `M` is `0`, repeats endlessly.