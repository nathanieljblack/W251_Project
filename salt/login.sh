# parse input arguments
usage() { echo "Usage: $0 [-u <string> softlayer username] "\
"[-k <string> softlayer api key] "\
"[-h <string> hostname of salt master]" 1>&2; exit 1; }

while getopts ":u:k:h:" opt; do
  case $opt in
    u) user="$OPTARG"
    ;;
    k) key="$OPTARG"
    ;;
    h) vs_hostname="$OPTARG"
    ;;
    *) usage
    ;;
  esac
done
shift $((OPTIND-1))

if [ -z "${user}" ] || [ -z "${key}" ] || [ -z "${vs_hostname}" ]; then
    usage
fi

masterdetails=$(curl 'https://'"${user}"':'"${key}"'@api.softlayer.com/rest/v3/SoftLayer_Account/VirtualGuests.json?objectMask=id;fullyQualifiedDomainName;hostname;domain;primaryIpAddress;operatingSystem.passwords' | jq -r '.[] | select (.hostname == "'"${vs_hostname}"'") |{fullyQualifiedDomainName,id,root_password: .operatingSystem.passwords[] | select(.username == "root").password,primaryIpAddress}')
root_pwd=$(echo $masterdetails | jq -r '.["root_password"]')
public_ip=$(echo $masterdetails | jq -r '.["primaryIpAddress"]')

echo $public_ip
echo $root_pwd

ssh root@$public_ip