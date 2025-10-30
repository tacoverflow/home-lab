#! /bin/bash -xe

cleanup_rules=$(iptables-save | grep '172.' | sed 's/-A/iptables -t nat -D/')
echo "$cleanup_rules" | while read rule; do
        $rule
done
